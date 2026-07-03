import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ChevronDown, ChevronUp, Menu, X } from 'lucide-react';
import { UI_CONFIG } from '../../config/ui';
import { MENU_ITEMS } from './menuData';

export const MobileMenu: React.FC = () => {
    const { t } = useTranslation('header');
    const [isOpen, setIsOpen] = useState(false);
    const [expandedKey, setExpandedKey] = useState<string | null>(null);

    const handleItemClick = (key: string, hasSubItems: boolean) => {
        if (hasSubItems) setExpandedKey(expandedKey === key ? null : key);
        else setIsOpen(false);
    };

    return (
        <div className="flex items-center">
            <button onClick={() => setIsOpen(!isOpen)} className={`flex items-center gap-2 ${UI_CONFIG.fonts.menuCompact} hover:text-white transition-colors`}>
                <span>{t('mobile_menu')}</span>
                {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            <div className={`absolute top-[4.5rem] left-0 w-full ${UI_CONFIG.header.backgroundClass} shadow-xl overflow-hidden transition-[max-height,opacity] duration-300 ease-out z-50 ${isOpen ? 'max-h-screen opacity-100' : 'max-h-0 opacity-0'}`}>
                <div className="flex flex-col p-4 gap-4 max-h-[calc(100vh-4.5rem)] overflow-y-auto">
                    {MENU_ITEMS.map(item => {
                        const hasSubItems = !!(item.subColumns && item.subColumns.length > 0);
                        return (
                            <div key={item.key} className="flex flex-col border-b border-blue-500/30 pb-2">
                                <button onClick={() => handleItemClick(item.key, hasSubItems)} className={`flex items-center justify-between w-full text-left ${UI_CONFIG.fonts.menuCompact} hover:text-white transition-colors py-2`}>
                                    {item.path && !hasSubItems ? <Link to={item.path} onClick={() => setIsOpen(false)} className="w-full">{t(item.labelKey)}</Link> : <span>{t(item.labelKey)}</span>}
                                    {hasSubItems && (expandedKey === item.key ? <ChevronUp size={20} /> : <ChevronDown size={20} />)}
                                </button>
                                {hasSubItems && (
                                    <div className={`grid transition-all duration-300 ease-out ${expandedKey === item.key ? 'grid-rows-[1fr] mt-2' : 'grid-rows-[0fr]'}`}>
                                        <div className="overflow-hidden flex flex-col gap-4 pl-4">
                                            {item.subColumns?.map((col, colIdx) => (
                                                <div key={colIdx} className="flex flex-col gap-4">
                                                    {col.groups.map((grp, grpIdx) => (
                                                        <div key={grpIdx} className="flex flex-col gap-1">
                                                            <span className="text-gray-800 font-bold text-xs mb-1">{t(grp.groupLabelKey)}</span>
                                                            {grp.items.map((sub, sIdx) => sub.external ? <a key={sIdx} href={sub.path} onClick={() => setIsOpen(false)} className={`py-1 hover:text-white ${UI_CONFIG.fonts.menuStandard}`}>{t(sub.labelKey)}</a> : <Link key={sIdx} to={sub.path} onClick={() => setIsOpen(false)} className={`py-1 hover:text-white ${UI_CONFIG.fonts.menuStandard}`}>{t(sub.labelKey)}</Link>)}
                                                        </div>
                                                    ))}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};