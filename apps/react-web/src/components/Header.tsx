import React, { useState, useRef, useLayoutEffect, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { UI_CONFIG } from '../config/ui';
import orgLogo from '../assets/saologo.png';

interface MenuItem { key: string; labelKey: string; path?: string; subItems?: SubMenuGroup[]; }
interface SubMenuGroup { groupLabelKey: string; items: { labelKey: string; path: string }[]; }

const MENU_ITEMS: MenuItem[] = [
    { key: 'home', labelKey: 'menu.home', path: '/' },
    {
        key: 'observations', labelKey: 'menu.observations',
        subItems: [{ groupLabelKey: 'menu.solar_obs', items: [{ labelKey: 'menu.latest_fast_acq', path: '/latest-observations' }] }]
    },
    { key: 'resources', labelKey: 'menu.resources', path: '/resources' },
    {
        key: 'about', labelKey: 'menu.about',
        subItems: [
            { groupLabelKey: 'menu.instrument', items: [{ labelKey: 'menu.telescope', path: '/telescope' }, { labelKey: 'menu.receivers', path: '/receivers' }] },
            { groupLabelKey: 'menu.science', items: [{ labelKey: 'menu.publications', path: '/publications' }] }
        ]
    },
    { key: 'contacts', labelKey: 'menu.contacts', path: '/contacts' },
];

export const Header: React.FC = () => {
    const { t, i18n } = useTranslation();
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const [activeMenu, setActiveMenu] = useState<string | null>(null);
    const [renderedMenuKey, setRenderedMenuKey] = useState<string | null>(null);
    const [isPanelOpen, setIsPanelOpen] = useState(false);
    const [contentHeight, setContentHeight] = useState(0);

    const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const mouseLocs = useRef<{ x: number; y: number }[]>([]);
    const contentRef = useRef<HTMLDivElement>(null);

    useEffect(() => { document.title = t('page_title'); }, [i18n.language, t]);

    useLayoutEffect(() => {
        if (isPanelOpen && contentRef.current) {
            setContentHeight(contentRef.current.scrollHeight);
        }
    }, [renderedMenuKey, isPanelOpen]);

    const handleMouseMove = (e: React.MouseEvent) => {
        mouseLocs.current.push({ x: e.clientX, y: e.clientY });
        if (mouseLocs.current.length > 3) mouseLocs.current.shift();
    };

    const handleMouseEnter = (key: string) => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current);

        const locs = mouseLocs.current;
        const isMovingDown = locs.length > 1 && locs[locs.length - 1].y > locs[0].y + 2;

        const targetItem = MENU_ITEMS.find(m => m.key === key);
        const hasSubItems = !!(targetItem && targetItem.subItems && targetItem.subItems.length > 0);

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

    const activeSubItems = MENU_ITEMS.find(m => m.key === renderedMenuKey)?.subItems;
    const appliedHeight = isPanelOpen ? contentHeight : 0;

    return (
        <header
            className="relative w-full text-gray-900 z-50"
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
        >
            {/* ФОН БЕЗ ПРОЗРАЧНОСТИ */}
            <div
                className={`absolute top-0 left-0 w-full ${UI_CONFIG.header.backgroundClass} transition-[height] duration-300 ease-out shadow-xl`}
                style={{ height: `calc(${UI_CONFIG.header.heightRem} + ${appliedHeight}px)` }}
            />

            {/* ГЛАВНАЯ ПОЛОСА */}
            <div className={`relative flex items-center justify-between ${UI_CONFIG.layout.pagePadding} ${UI_CONFIG.header.heightClass}`}>

                <Link to="/" className="flex items-center gap-4 hover:opacity-80 transition-opacity">
                    <img src={orgLogo} alt="Логотип САО РАН" className="h-16 w-auto object-contain shrink-0" />

                    <div className={`${UI_CONFIG.fonts.orgName} w-max text-center`}>
                        {t('orgName_line1')}<br/>
                        {t('orgName_line2')}<br/>
                        {t('orgName_line3')}
                    </div>
                </Link>

                <nav className="absolute left-1/2 transform -translate-x-1/2 h-full hidden lg:flex items-center">
                    <ul className={`flex items-center gap-12 ${UI_CONFIG.fonts.menuStandard}`}>
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

            {/* content container */}
            <div
                className="absolute left-0 w-full overflow-hidden transition-[height,opacity] duration-300 ease-out"
                style={{
                    top: UI_CONFIG.header.heightRem,
                    height: `${appliedHeight}px`,
                    opacity: isPanelOpen ? 1 : 0
                }}
            >
                <div ref={contentRef} className="py-6 max-w-4xl mx-auto flex gap-16 justify-center">
                    {activeSubItems?.map((group, idx) => (
                        <div key={idx} className="flex flex-col gap-2">
                            <span className="text-gray-700 font-semibold text-sm mb-2">{t(group.groupLabelKey)}</span>
                            {group.items.map(subItem => (
                                <Link key={subItem.path} to={subItem.path} className={`hover:text-white transition-colors ${UI_CONFIG.fonts.menuStandard}`}>
                                    {t(subItem.labelKey)}
                                </Link>
                            ))}
                        </div>
                    ))}
                </div>
            </div>
        </header>
    );
};