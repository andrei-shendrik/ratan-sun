import React from 'react';
import { useTranslation } from 'react-i18next';

export const Footer: React.FC = () => {
    const { t } = useTranslation();
    const currentYear = new Date().getFullYear();

    return (
        <footer className="w-full py-6 border-t border-gray-300 bg-gray-50 text-center text-gray-500 text-sm">
            © {currentYear} {t('footer_text')}
        </footer>
    );
};