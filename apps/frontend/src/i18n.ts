import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import commonRu from './locales/ru/common.json';
import headerRu from './locales/ru/header.json';
import commonEn from './locales/en/common.json';
import headerEn from './locales/en/header.json';

void i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
    resources: {
      ru: {
        common: commonRu,
        header: headerRu
      },
      en: {
        common: commonEn,
        header: headerEn
      }
    },
    fallbackLng: 'ru',
    defaultNS: 'common',
    interpolation: { escapeValue: false },
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'ratan_sun_lang',
      caches: ['localStorage'],
    }
    });

export default i18n;