import React, { useState, useRef, useLayoutEffect, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { UI_CONFIG } from '../config/ui';
import orgLogo from '../assets/saologo.png';

interface SubMenuItem { labelKey: string; path: string; external?: boolean; }
interface SubMenuGroup { groupLabelKey: string; items: SubMenuItem[]; }
interface SubMenuColumn { groups: SubMenuGroup[]; }
interface MenuItem { key: string; labelKey: string; path?: string; subColumns?: SubMenuColumn[]; }

const MENU_ITEMS: MenuItem[] = [
    { key: 'home', labelKey: 'menu.home', path: '/' },
    {
        key: 'observations', labelKey: 'menu.observations.title',
        subColumns: [
            { // Колонка 1
                groups: [{
                    groupLabelKey: 'menu.observations.groups.solar',
                    items: [
                        { labelKey: 'menu.observations.items.latest', path: '/latest-observations' },
                        { labelKey: 'menu.observations.items.archive', path: 'https://solar.sao.ru/data', external: true },
                        { labelKey: 'menu.observations.items.schedule', path: '/observation-schedule' }
                    ]
                }]
            },
            { // Колонка 2
                groups: [{
                    groupLabelKey: 'menu.observations.groups.selection',
                    items: [
                        { labelKey: 'menu.observations.items.fast_acq_1_3', path: '/select-of-observation-fast-acq-1-3ghz' },
                        { labelKey: 'menu.observations.items.sspc', path: '/select-of-observation-sspc-3-18ghz' }
                    ]
                }]
            }
        ]
    },
    {
        key: 'resources', labelKey: 'menu.resources.title',
        subColumns: [{
            groups: [
                {
                    groupLabelKey: 'menu.resources.groups.general',
                    items: [
                        { labelKey: 'menu.resources.items.forecast', path: 'http://spbf.sao.ru/prognoz', external: true },
                        { labelKey: 'menu.resources.items.jets', path: '/coronal-jets-catalog', external: true },
                        { labelKey: 'menu.resources.items.dataview', path: '/dataview/', external: true }
                    ]
                },
                {
                    groupLabelKey: 'menu.resources.groups.software',
                    items: [
                        { labelKey: 'menu.resources.items.ratanpy', path: 'https://github.com/andrei-shendrik/ratanpy', external: true }
                    ]
                }
            ]
        }]
    },
    {
        key: 'about', labelKey: 'menu.about.title',
        subColumns: [
            {
                groups: [{
                    groupLabelKey: 'menu.about.groups.instrument',
                    items: [
                        { labelKey: 'menu.about.items.telescope', path: '/telescope' },
                        { labelKey: 'menu.about.items.receivers', path: '/receivers' }
                    ]
                }]
            },
            {
                groups: [
                    {
                        groupLabelKey: 'menu.about.groups.about_us',
                        items: [{ labelKey: 'menu.about.items.branch', path: '/about-us' }]
                    },
                    {
                        groupLabelKey: 'menu.about.groups.science',
                        items: [{ labelKey: 'menu.about.items.publications', path: '/publications' }]
                    }
                ]
            }
        ]
    },
    { key: 'contacts', labelKey: 'menu.contacts', path: '/contacts' },
];

export const Header: React.FC = () => {
    const { t, i18n } = useTranslation('header');
    const { t: tCommon } = useTranslation('common');

    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [activeMenu, setActiveMenu] = useState<string | null>(null);
    const [renderedMenuKey, setRenderedMenuKey] = useState<string | null>(null);
    const [isPanelOpen, setIsPanelOpen] = useState(false);
    const [contentHeight, setContentHeight] = useState(0);

    // НОВОЕ: Состояние для хранения отступа слева
    const [dropdownPaddingLeft, setDropdownPaddingLeft] = useState<number | null>(null);

    const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const mouseLocs = useRef<{ x: number; y: number }[]>([]);

    const navRef = useRef<HTMLUListElement>(null);
    const contentRef = useRef<HTMLDivElement>(null);
    const innerContentRef = useRef<HTMLDivElement>(null);

    useEffect(() => { document.title = tCommon('page_title'); }, [i18n.language, tCommon]);

    // расчет выравнивания
    const calculateAlignment = () => {
        if (navRef.current && innerContentRef.current) {
            // navRect содержит координаты и размеры менюбара
            const navRect = navRef.current.getBoundingClientRect();
            // ширина контента выпадающего подменю
            const contentWidth = innerContentRef.current.getBoundingClientRect().width;

            if (contentWidth <= navRect.width) {
                // выравнивание по левому краю
                setDropdownPaddingLeft(navRect.left);
            } else {
                // если шире -- выравнивание по центру
                setDropdownPaddingLeft(null);
            }
        }
    };

    useLayoutEffect(() => {
        if (isPanelOpen && contentRef.current) {
            setContentHeight(contentRef.current.scrollHeight);
            calculateAlignment();
        }
    }, [renderedMenuKey, isPanelOpen]);

    // пересчет при ресайзе окна
    useEffect(() => {
        window.addEventListener('resize', calculateAlignment);
        return () => window.removeEventListener('resize', calculateAlignment);
    }, []);

    const handleMouseMove = (e: React.MouseEvent) => {
        mouseLocs.current.push({ x: e.clientX, y: e.clientY });
        if (mouseLocs.current.length > 3) mouseLocs.current.shift();
    };

    const handleMouseEnter = (key: string) => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        const locs = mouseLocs.current;
        const isMovingDown = locs.length > 1 && locs[locs.length - 1].y > locs[0].y + 2;
        const targetItem = MENU_ITEMS.find(m => m.key === key);
        const hasSubItems = !!(targetItem && targetItem.subColumns && targetItem.subColumns.length > 0);

        const applyState = () => {
            setActiveMenu(key);
            if (hasSubItems) {
                setRenderedMenuKey(key);
                setIsPanelOpen(true);
            } else {
                setIsPanelOpen(false);
            }
        };

        if (isPanelOpen && isMovingDown) {
            timeoutRef.current = setTimeout(applyState, 300);
        } else {
            applyState();
        }
    };

    const handleMouseLeave = () => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        timeoutRef.current = setTimeout(() => {
            setIsPanelOpen(false);
            setActiveMenu(null);
        }, 300);
    };

    const toggleLang = () => i18n.changeLanguage(i18n.language === 'ru' ? 'en' : 'ru');
    const activeSubColumns = MENU_ITEMS.find(m => m.key === renderedMenuKey)?.subColumns;
    const appliedHeight = isPanelOpen ? contentHeight : 0;

    return (
        <header
            className="relative w-full text-gray-900 z-50"
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
        >
            <div
                className={`absolute top-0 left-0 w-full ${UI_CONFIG.header.backgroundClass} transition-[height] duration-300 ease-out shadow-xl`}
                style={{ height: `calc(${UI_CONFIG.header.heightRem} + ${appliedHeight}px)` }}
            />

            <div className={`relative flex items-center justify-between ${UI_CONFIG.layout.pagePadding} ${UI_CONFIG.header.heightClass}`}>

                <Link to="/" className="flex items-center gap-4 hover:opacity-80 transition-opacity">
                    <img src={orgLogo} alt="Логотип САО РАН" className="h-16 w-auto object-contain shrink-0" />
                    <div className={`${UI_CONFIG.fonts.orgName} w-max text-center`}>
                        {t('orgName.line1')}<br/>
                        {t('orgName.line2')}<br/>
                        {t('orgName.line3')}
                    </div>
                </Link>

                <nav className="absolute left-1/2 transform -translate-x-1/2 h-full hidden lg:flex items-center">
                    {/* НОВОЕ: Повесили ref на ul, чтобы знать координаты менюбара */}
                    <ul ref={navRef} className={`flex items-center gap-12 ${UI_CONFIG.fonts.menuStandard}`}>
                        {MENU_ITEMS.map(item => (
                            <li
                                key={item.key}
                                className="py-2 cursor-pointer group"
                                onMouseEnter={() => handleMouseEnter(item.key)}
                            >
                                {item.path ? (
                                    <Link to={item.path} className={`transition-colors ${isPanelOpen && activeMenu === item.key ? 'text-white' : 'group-hover:text-white'}`}>
                                        {t(item.labelKey)}
                                    </Link>
                                ) : (
                                    <span className={`transition-colors ${isPanelOpen && activeMenu === item.key ? 'text-white' : 'group-hover:text-white'}`}>
                                        {t(item.labelKey)}
                                    </span>
                                )}
                            </li>
                        ))}
                    </ul>
                </nav>

                <div className={`flex items-center gap-6 ${UI_CONFIG.fonts.controls}`}>
                    <button onClick={() => setIsLoggedIn(!isLoggedIn)} className="flex items-center gap-2 hover:text-white transition-colors">
                        <User size={20} />
                        <span>{isLoggedIn ? t('auth.logout') : t('auth.login')}</span>
                    </button>
                    <button onClick={toggleLang} className="hover:text-white transition-colors w-6 text-center">
                        {i18n.language === 'ru' ? 'EN' : 'RU'}
                    </button>
                </div>
            </div>

            <div
                className="absolute left-0 w-full overflow-hidden transition-[height,opacity] duration-300 ease-out"
                style={{ top: UI_CONFIG.header.heightRem, height: `${appliedHeight}px`, opacity: isPanelOpen ? 1 : 0 }}
            >
                <div
                    ref={contentRef}
                    className={`w-full ${dropdownPaddingLeft !== null ? 'flex justify-start' : 'flex justify-center'}`}
                    style={{ paddingLeft: dropdownPaddingLeft !== null ? `${dropdownPaddingLeft}px` : '0px' }}
                >
                    <div ref={innerContentRef} className="py-6 flex gap-20 w-max">
                        {activeSubColumns?.map((col, colIdx) => (
                            <div key={colIdx} className="flex flex-col gap-6">
                                {col.groups.map((group, grpIdx) => (
                                    <div key={grpIdx} className="flex flex-col gap-2">
                                        <span className="text-gray-700 font-semibold text-sm mb-2">{t(group.groupLabelKey)}</span>
                                        {group.items.map((subItem, itemIdx) => (
                                            subItem.external ? (
                                                <a
                                                    key={itemIdx}
                                                    href={subItem.path}
                                                    target={subItem.path.startsWith('http') ? '_blank' : '_self'}
                                                    rel={subItem.path.startsWith('http') ? 'noopener noreferrer' : undefined}
                                                    className={`hover:text-white transition-colors ${UI_CONFIG.fonts.menuStandard}`}
                                                >
                                                    {t(subItem.labelKey)}
                                                </a>
                                            ) : (
                                                <Link
                                                    key={itemIdx}
                                                    to={subItem.path}
                                                    className={`hover:text-white transition-colors ${UI_CONFIG.fonts.menuStandard}`}
                                                >
                                                    {t(subItem.labelKey)}
                                                </Link>
                                            )
                                        ))}
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </header>
    );
};