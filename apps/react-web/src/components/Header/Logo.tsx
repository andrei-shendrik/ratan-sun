import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { UI_CONFIG } from '../../config/ui';
import orgLogo from '../../assets/saologo.png';

export const Logo: React.FC<{ showText: boolean }> = ({ showText }) => {
    const { t } = useTranslation('header');
    const fullOrgName = `${t('orgName.line1')} ${t('orgName.line2')} ${t('orgName.line3')}`;

    return (
        <Link to="/" className="flex items-center gap-4 hover:opacity-80 transition-opacity flex-shrink-0" title={!showText ? fullOrgName : undefined}>
            <img src={orgLogo} alt="Логотип САО РАН" className="h-16 w-auto object-contain shrink-0" />

            {showText && (
                <div className={`${UI_CONFIG.fonts.orgName} whitespace-nowrap text-center`}>
                    {t('orgName.line1')}<br/>
                    {t('orgName.line2')}<br/>
                    {t('orgName.line3')}
                </div>
            )}
        </Link>
    );
};