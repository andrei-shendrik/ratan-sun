import { useState, useRef, useLayoutEffect, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { UI_CONFIG } from '../../config/ui';

import { Logo } from './Logo';
import { DesktopMenu } from './DesktopMenu';
import { MobileMenu } from './MobileMenu';
import { useHeaderLayout } from './useHeaderLayout';
import { MENU_ITEMS } from './menuData';

export const Header = () => {
    const { t, i18n } = useTranslation('header');
    const { t: tCommon } = useTranslation('common');
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const [activeMenu, setActiveMenu] = useState<string | null>(null);
    const [renderedMenuKey, setRenderedMenuKey] = useState<string | null>(null);
    const [isPanelOpen, setIsPanelOpen] = useState(false);

    const [contentHeight, setContentHeight] = useState(0);
    const [panelPaddingLeft, setPanelPaddingLeft] = useState<number | null>(null);

    const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const mouseLocs = useRef<{ x: number; y: number }[]>([]);

    const containerRef = useRef<HTMLElement | null>(null);
    const ghostContainerRef = useRef<HTMLDivElement | null>(null);
    const logoFullRef = useRef<HTMLDivElement | null>(null);
    const logoSmallRef = useRef<HTMLDivElement | null>(null);
    const ghostDesktopMenuRef = useRef<HTMLUListElement | null>(null);
    const mobileMenuRef = useRef<HTMLDivElement | null>(null);
    const rightControlsRef = useRef<HTMLDivElement | null>(null);

    const actualDesktopMenuRef = useRef<HTMLUListElement | null>(null);
    const innerContentRef = useRef<HTMLDivElement | null>(null);

    const layout = useHeaderLayout(
        containerRef, ghostContainerRef, logoFullRef, logoSmallRef, ghostDesktopMenuRef, mobileMenuRef, rightControlsRef,
        UI_CONFIG.header.minGap, UI_CONFIG.header.paddingNormal, UI_CONFIG.header.paddingMinimal
    );

    useEffect(() => { document.title = tCommon('page_title'); }, [i18n.language, tCommon]);

    useLayoutEffect(() => {
        if (isPanelOpen && innerContentRef.current && actualDesktopMenuRef.current) {
            setContentHeight(innerContentRef.current.scrollHeight);

            const navRect = actualDesktopMenuRef.current.getBoundingClientRect();
            const contentWidth = innerContentRef.current.offsetWidth;
            const windowWidth = document.documentElement.clientWidth;

            if (navRect.left + contentWidth <= windowWidth - UI_CONFIG.header.paddingNormal) {
                setPanelPaddingLeft(navRect.left);
            } else {
                setPanelPaddingLeft(null);
            }
        }
    }, [renderedMenuKey, isPanelOpen, layout]);

    const handleMouseMove = (e: React.MouseEvent) => {
        mouseLocs.current.push({ x: e.clientX, y: e.clientY });
        if (mouseLocs.current.length > 3) mouseLocs.current.shift();
    };

    const handleMouseEnterDesktop = (key: string) => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        const isMovingDown = mouseLocs.current.length > 1 && mouseLocs.current[mouseLocs.current.length - 1].y > mouseLocs.current[0].y + 2;
        const targetItem = MENU_ITEMS.find(m => m.key === key);
        const hasSubItems = !!(targetItem && targetItem.subColumns && targetItem.subColumns.length > 0);

        const applyState = () => {
            setActiveMenu(key);
            if (hasSubItems) {
                setRenderedMenuKey(key);
                setIsPanelOpen(true);
            } else setIsPanelOpen(false);
        };

        if (isPanelOpen && isMovingDown) timeoutRef.current = setTimeout(applyState, 300);
        else applyState();
    };

    const handleMouseLeaveHeader = () => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        timeoutRef.current = setTimeout(() => { setIsPanelOpen(false); setActiveMenu(null); }, 300);
    };

    const closeMenu = () => { setIsPanelOpen(false); setActiveMenu(null); };

    const activeSubColumns = MENU_ITEMS.find(m => m.key === renderedMenuKey)?.subColumns;
    const appliedHeight = isPanelOpen ? contentHeight : 0;

    return (
        <header ref={containerRef} className="relative w-full text-gray-900 z-50" onMouseMove={handleMouseMove} onMouseLeave={handleMouseLeaveHeader}>

            <div ref={ghostContainerRef} className="absolute top-[-9999px] left-0 invisible flex opacity-0 pointer-events-none whitespace-nowrap w-max">
                <div ref={logoFullRef} className="w-max"><Logo showText={true} /></div>
                <div ref={logoSmallRef} className="w-max"><Logo showText={false} /></div>
                <div className="w-max"><DesktopMenu ref={ghostDesktopMenuRef} activeMenu={null} isPanelOpen={false} onMouseEnter={()=>{}} closeMenu={()=>{}} /></div>
                <div ref={mobileMenuRef} className="w-max"><MobileMenu /></div>
                <div ref={rightControlsRef} className="w-max">
                    <div className={`flex items-center gap-4 lg:gap-6 ${UI_CONFIG.fonts.controls}`}>
                        <button className="flex items-center gap-2"><User size={20}/><span className="hidden sm:inline">{isLoggedIn ? t('auth.logout') : t('auth.login')}</span></button>
                        <button className="w-6 text-center">{i18n.language === 'ru' ? 'EN' : 'RU'}</button>
                    </div>
                </div>
            </div>

            {/* фон */}
            <div className={`absolute top-0 left-0 w-full ${UI_CONFIG.header.backgroundClass} transition-[height] duration-300 ease-out shadow-xl -z-10`} style={{ height: `calc(${UI_CONFIG.header.heightRem} + ${appliedHeight}px)` }} />

            {/* шапка */}
            <div className={`relative flex items-center h-[4.5rem]`} style={{ paddingLeft: `${layout.paddingPx}px`, paddingRight: `${layout.paddingPx}px` }}>

                {layout.layoutType === 'absolute-center' ? (
                    <>
                        <div className="flex-1 flex justify-start min-w-0"> <Logo showText={layout.showOrgName} /> </div>
                        <div className="absolute left-1/2 -translate-x-1/2">
                            {layout.showDesktopMenu ? <DesktopMenu ref={actualDesktopMenuRef} activeMenu={activeMenu} isPanelOpen={isPanelOpen} onMouseEnter={handleMouseEnterDesktop} closeMenu={closeMenu} /> : <MobileMenu />}
                        </div>
                        <div className="flex-1 flex justify-end min-w-0">
                            <div className={`flex items-center gap-4 lg:gap-6 ${UI_CONFIG.fonts.controls}`}>
                                <button onClick={() => setIsLoggedIn(!isLoggedIn)} className="flex items-center gap-2 hover:text-white transition-colors"><User size={20} /><span className="hidden sm:inline">{isLoggedIn ? t('auth.logout') : t('auth.login')}</span></button>
                                <button onClick={() => i18n.changeLanguage(i18n.language === 'ru' ? 'en' : 'ru')} className="hover:text-white transition-colors w-6 text-center">{i18n.language === 'ru' ? 'EN' : 'RU'}</button>
                            </div>
                        </div>
                    </>
                ) : (
                    <>
                        <div className="flex-none flex justify-start min-w-0"> <Logo showText={layout.showOrgName} /> </div>
                        <div className="flex-1 flex justify-center min-w-0">
                            {layout.showDesktopMenu ? <DesktopMenu ref={actualDesktopMenuRef} activeMenu={activeMenu} isPanelOpen={isPanelOpen} onMouseEnter={handleMouseEnterDesktop} closeMenu={closeMenu} /> : <MobileMenu />}
                        </div>
                        <div className="flex-none flex justify-end min-w-0">
                            <div className={`flex items-center gap-4 lg:gap-6 ${UI_CONFIG.fonts.controls}`}>
                                <button onClick={() => setIsLoggedIn(!isLoggedIn)} className="flex items-center gap-2 hover:text-white transition-colors"><User size={20} /><span className="hidden sm:inline">{isLoggedIn ? t('auth.logout') : t('auth.login')}</span></button>
                                <button onClick={() => i18n.changeLanguage(i18n.language === 'ru' ? 'en' : 'ru')} className="hover:text-white transition-colors w-6 text-center">{i18n.language === 'ru' ? 'EN' : 'RU'}</button>
                            </div>
                        </div>
                    </>
                )}
            </div>

            {/* шторка */}
            <div className="absolute left-0 w-full overflow-hidden transition-[height,opacity] duration-300 ease-out z-10" style={{ top: UI_CONFIG.header.heightRem, height: `${appliedHeight}px`, opacity: isPanelOpen ? 1 : 0 }}>
                <div className={`w-full flex ${panelPaddingLeft !== null ? 'justify-start' : 'justify-center'}`} style={{ paddingLeft: panelPaddingLeft !== null ? `${panelPaddingLeft}px` : '0px' }}>
                    <div ref={innerContentRef} className="py-6 flex gap-20 w-max">
                        {activeSubColumns?.map((col, colIdx) => (
                            <div key={colIdx} className="flex flex-col gap-6">
                                {col.groups.map((group, grpIdx) => (
                                    <div key={grpIdx} className="flex flex-col gap-2">
                                        <span className="text-gray-700 font-semibold text-sm mb-2">{t(group.groupLabelKey)}</span>
                                        {group.items.map((subItem, itemIdx) => (
                                            subItem.external ? (
                                                <a key={itemIdx} href={subItem.path} onClick={closeMenu} target={subItem.path.startsWith('http') ? '_blank' : '_self'} rel="noopener noreferrer" className={`hover:text-white transition-colors ${UI_CONFIG.fonts.menuStandard}`}>{t(subItem.labelKey)}</a>
                                            ) : (
                                                <Link key={itemIdx} to={subItem.path} onClick={closeMenu} className={`hover:text-white transition-colors ${UI_CONFIG.fonts.menuStandard}`}>{t(subItem.labelKey)}</Link>
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