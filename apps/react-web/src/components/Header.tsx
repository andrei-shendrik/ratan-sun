import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';

const t = (key: string) => key;
const i18n = { language: 'ru', changeLanguage: (l: string) => {} };

interface MenuItem {
    key: string;
    label: string;
    path?: string;
    subItems?: SubMenuGroup[];
}

interface SubMenuGroup {
    groupLabel: string;
    items: { label: string; path: string }[];
}

export const Header: React.FC = () => {
    const [isHoveredMenu, setIsHoveredMenu] = useState<string | null>(null);
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    const menuItems: MenuItem[] = [
        { key: 'home', label: 'Главная', path: '/' },
        {
            key: 'observations', label: 'Наблюдения',
            subItems: [
                {
                    groupLabel: 'Солнечные наблюдения',
                    items: [
                        { label: 'Обзор данных последних наблюдений', path: '/latest-observations' }
                    ]
                }
            ]
        },
        { key: 'resources', label: 'Ресурсы', path: '/resources' },
        {
            key: 'about', label: 'О нас',
            subItems: [
                {
                    groupLabel: 'Инструмент:',
                    items: [
                        { label: 'Телескоп', path: '/telescope' },
                        { label: 'Приемные комплексы', path: '/receivers' },
                    ]
                },
                {
                    groupLabel: 'Научная деятельность:',
                    items: [
                        { label: 'Публикации', path: '/publications' },
                    ]
                }
            ]
        },
        { key: 'contacts', label: 'Контакты', path: '/contacts' },
    ];

    const activeSubItems = menuItems.find(m => m.key === isHoveredMenu)?.subItems;

    return (
        <header className="relative w-full bg-blue-400 text-gray-900 transition-all duration-300 z-50">
            <div className="flex items-center justify-between px-8 h-24">

                <Link to="/" className="flex items-center gap-4 hover:opacity-80 transition-opacity">
                    <div className="h-16 w-16 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs">ЛОГО</div>
                    <div className="text-sm font-bold uppercase leading-tight w-[13rem]">
                        Специальная Астрофизическая Обсерватория<br/>
                        Российской Академии Наук
                    </div>
                </Link>

                <nav className="absolute left-1/2 transform -translate-x-1/2 h-full">
                    <ul className="flex items-center h-full gap-8 text-[14px]">
                        {menuItems.map(item => (
                            <li
                                key={item.key}
                                className="h-full flex items-center"
                                onMouseEnter={() => setIsHoveredMenu(item.key)}
                                onMouseLeave={() => setIsHoveredMenu(null)}
                            >
                                {item.path ? (
                                    <Link to={item.path} className="hover:text-white transition-colors h-full flex items-center">
                                        {item.label}
                                    </Link>
                                ) : (
                                    <span className="cursor-pointer hover:text-white transition-colors h-full flex items-center">
                                        {item.label}
                                    </span>
                                )}
                            </li>
                        ))}
                    </ul>
                </nav>

                <div className="flex items-center gap-6">
                    <button onClick={() => setIsLoggedIn(!isLoggedIn)} className="flex items-center gap-2 hover:text-white transition-colors">
                        <User size={20} />
                        <span>{isLoggedIn ? 'Выйти' : 'Войти'}</span>
                    </button>
                    <button className="font-bold hover:text-white transition-colors">
                        EN
                    </button>
                </div>
            </div>

            <div
                className={`absolute top-full left-0 w-full bg-blue-400 overflow-hidden transition-all duration-300 ease-in-out ${activeSubItems ? 'max-h-96 py-6 shadow-lg' : 'max-h-0 py-0'}`}
                onMouseEnter={() => setIsHoveredMenu(isHoveredMenu)}
                onMouseLeave={() => setIsHoveredMenu(null)}
            >
                <div className="max-w-4xl mx-auto flex gap-16 justify-center">
                    {activeSubItems?.map((group, idx) => (
                        <div key={idx} className="flex flex-col gap-2">
                            <span className="text-gray-700 font-semibold text-sm mb-2">{group.groupLabel}</span>
                            {group.items.map(subItem => (
                                <Link key={subItem.path} to={subItem.path} className="text-[14px] hover:text-white transition-colors">
                                    {subItem.label}
                                </Link>
                            ))}
                        </div>
                    ))}
                </div>
            </div>
        </header>
    );
};