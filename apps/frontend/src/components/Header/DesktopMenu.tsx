import { forwardRef } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { UI_CONFIG } from '../../config/ui';
import { MENU_ITEMS } from './menuData';

interface Props {
    activeMenu: string | null;
    isPanelOpen: boolean;
    onMouseEnter: (key: string) => void;
    closeMenu: () => void;
}

export const DesktopMenu = forwardRef<HTMLUListElement, Props>(
    ({ activeMenu, isPanelOpen, onMouseEnter, closeMenu }, ref) => {
        const { t } = useTranslation('header');
        return (
            <ul ref={ref} className={`flex items-center gap-6 xl:gap-12 ${UI_CONFIG.fonts.menuStandard}`}>
                {MENU_ITEMS.map(item => (
                    <li key={item.key} className="py-2 cursor-pointer group whitespace-nowrap" onMouseEnter={() => onMouseEnter(item.key)}>
                        {item.path ? (
                            <Link to={item.path} onClick={closeMenu} className={`transition-colors ${isPanelOpen && activeMenu === item.key ? 'text-white' : 'group-hover:text-white'}`}>
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
        );
    }
);