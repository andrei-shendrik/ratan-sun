import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import commonRu from './locales/ru/common.json';
import headerRu from './locales/ru/header.json';
import commonEn from './locales/en/common.json';
import headerEn from './locales/en/header.json';

void i18n
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
    lng: 'ru',
    fallbackLng: 'ru',
    // Указываем, какой файл использовать по умолчанию (если разработчик не указал namespace явно)
    defaultNS: 'common',
    interpolation: { escapeValue: false }
  });

export default i18n;