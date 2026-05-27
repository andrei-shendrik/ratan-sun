import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import ru from './locales/ru/ru.json';
import en from './locales/en/en.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      ru: { translation: ru },
      en: { translation: en }
    },
    lng: 'ru', // язык по умолчанию
    fallbackLng: 'ru',
    interpolation: { escapeValue: false }
  });

export default i18n;