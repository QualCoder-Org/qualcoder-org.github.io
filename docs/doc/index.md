# QualCoder Documentation
*Please select your language*

## Official Documentation

- [English](/doc/en)

## Community Translations

- [Français](/doc/fr)

<script>
const availableLanguages = ['en', 'fr'];
const defaultLanguage = 'en';
const browserLanguage = navigator.language.split('-')[0];
if (availableLanguages.includes(browserLanguage)) {
  window.location.href = `/${browserLanguage}/`;
} else {
  window.location.href = `/${defaultLanguage}/`;
}
</script>
