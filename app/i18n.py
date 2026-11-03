"""Internationalisation Doğruluk — 14 langues.

Langues couvertes (demande utilisateur 2026-11-05) :
  français, arabe, anglais, italien, espagnol, portugais
  + toutes les langues turciques : turc, azéri, kazakh, kirghize, ouzbek,
    turkmène, tatar, bachkir (le yakoute et le tchouvache restent couverts
    par le turcique de base si besoin).

Fonctionnement :
  - dictionnaire TR par défaut (turc), traductions complètes fr/en,
    partielles it/es/pt ; les clés manquantes retombent sur l'anglais.
  - détection automatique : préférence navigateur, puis cookie `lang`,
    puis variable d'environnement VDF_LANG.
  - l'arabe est affiché en RTL (droite à gauche).

Les textes techniques des exports (en-têtes de colonnes) restent en français
pour garantir la compatibilité avec Point.P et les fournisseurs francophones.
"""
from __future__ import annotations

import os

DEFAULT_LANG = os.environ.get("VDF_LANG", "tr")

RTL_LANGS = {"ar"}

# Clés -> {lang: texte}. Les clés absentes d'une langue retombent sur 'en',
# puis sur la clé elle-même.
MESSAGES: dict[str, dict[str, str]] = {
    # ---- marque / navigation ----
    "tagline": {
        "fr": "Vérification devis & factures, tous fournisseurs",
        "en": "Quote & invoice checking, all suppliers",
        "it": "Verifica preventivi e fatture, tutti i fornitori",
        "es": "Verificación de presupuestos y facturas, todos los proveedores",
        "pt": "Verificação de orçamentos e faturas, todos os fornecedores",
        "ar": "التحقق من العروض والفواتير، لجميع الموردين",
        "tr": "Teklif ve fatura denetimi, tüm tedarikçiler",
        "az": "Təklif və faktura yoxlaması, bütün təchizatçılar",
        "kk": "Барлық жеткізушілер бойынша шарттар мен фактураларды тексеру",
        "ky": "Бардык жеткирүүчүлөр боюнча сунуштардын жана эсеп-фактуралардын текшерилиши",
        "uz": "Barcha yetkazib beruvchilar bo'yicha taklif va fakturalarni tekshirish",
        "tk": "Ähli üpjün edijiler boýunça teklipleriň we hasap-fakturalaryň barlagy",
        "tt": "Барлык тәэмин итүчеләр буенча тәкъдимнәрне һәм фактураны тикшерү",
        "ba": "Бөтә етештереүселәр буйынса тәҡдимдәрҙе һәм фактураларҙы тикшереү",
    },
    "nav_dashboard": {
        "fr": "Tableau de bord", "en": "Dashboard", "it": "Cruscotto",
        "es": "Panel", "pt": "Painel", "ar": "لوحة القيادة",
        "tr": "Kontrol Paneli", "az": "İdarə paneli", "kk": "Бақылау тақтасы",
        "ky": "Башкаруу тактасы", "uz": "Boshqaruv paneli", "tk": "Dolandyryş paneli",
        "tt": "Идарә панеле", "ba": "Идарә панеле",
    },
    "nav_sites": {
        "fr": "Chantiers", "en": "Job sites", "it": "Cantieri", "es": "Obras",
        "pt": "Obras", "ar": "ورش العمل", "tr": "Şantiyeler", "az": "Şantiyelər",
        "kk": "Құрылыс алаңдары", "ky": "Курулуш аянтчалары", "uz": "Qurilish maydonlari",
        "tk": "Gurluşik meýdançalary", "tt": "Шөҗәтмәләр", "ba": "Шөжәгалар",
    },
    "nav_export_ecarts": {
        "fr": "Export écarts (.xlsx)", "en": "Export discrepancies (.xlsx)",
        "it": "Esporta scostamenti (.xlsx)", "es": "Exportar desviaciones (.xlsx)",
        "pt": "Exportar divergências (.xlsx)", "ar": "تصدير الفروقات (.xlsx)",
        "tr": "Farkları dışa aktar (.xlsx)", "az": "Fərqləri ixrac et (.xlsx)",
        "kk": "Айырмашылықтарды экспорттау (.xlsx)", "ky": "Айырмачылыктарды экспорттоо (.xlsx)",
        "uz": "Farqlarni eksport qilish (.xlsx)", "tk": "Tapawutlary eksport etmek (.xlsx)",
        "tt": "Аермаларны экспортлау (.xlsx)", "ba": "Айырмаларҙы экспортлау (.xlsx)",
    },
    "nav_export_chantiers": {
        "fr": "Export chantiers (.xlsx)", "en": "Export job sites (.xlsx)",
        "it": "Esporta cantieri (.xlsx)", "es": "Exportar obras (.xlsx)",
        "pt": "Exportar obras (.xlsx)", "ar": "تصدير الورش (.xlsx)",
        "tr": "Şantiyeleri dışa aktar (.xlsx)", "az": "Şantiyeleri ixrac et (.xlsx)",
        "kk": "Алаңдарды экспорттау (.xlsx)", "ky": "Аянтчаларды экспорттоо (.xlsx)",
        "uz": "Maydonlarni eksport qilish (.xlsx)", "tk": "Meýdançalary eksport etmek (.xlsx)",
        "tt": "Шөҗәтмәләрне экспортлау (.xlsx)", "ba": "Шөжәгаларҙы экспортлау (.xlsx)",
    },
    # ---- pied de page / mentions ----
    "footer_edition": {
        "fr": "édition", "en": "edition", "it": "edizione", "es": "edición",
        "pt": "edição", "ar": "الإصدار", "tr": "sürüm", "az": "versiya",
        "kk": "нұсқа", "ky": "версия", "uz": "versiyasi", "tk": "wersiýasy",
        "tt": "версия", "ba": "версия",
    },
    "public": {"fr": "publique", "en": "public", "it": "pubblica", "es": "pública",
               "pt": "pública", "ar": "عام", "tr": "genel", "az": "pulsuz",
               "kk": "ашық", "ky": "ачык", "uz": "ochiq", "tk": "açyk",
               "tt": "ачык", "ba": "асыҡ"},
    "credits": {
        "fr": "Crédits", "en": "Credits", "it": "Crediti", "es": "Créditos",
        "pt": "Créditos", "ar": "الحقوق", "tr": "Katkılar", "az": "Töhfələr",
        "kk": "Үлестер", "ky": "Салымдар", "uz": "Hissalar", "tk": "Goşantlar",
        "tt": "Кертентемләр", "ba": "Өлөштәр",
    },
    "contact": {
        "fr": "contact", "en": "contact", "it": "contatto", "es": "contacto",
        "pt": "contato", "ar": "اتصال", "tr": "iletişim", "az": "əlaqə",
        "kk": "байланыс", "ky": "байланыш", "uz": "aloqa", "tk": "aragatnaşyk",
        "tt": "элемент", "ba": "бәйләнеш",
    },
    "legal_mentions": {
        "fr": "Mentions légales", "en": "Legal notice", "it": "Note legali",
        "es": "Aviso legal", "pt": "Avisos legais", "ar": "إشعارات قانونية",
        "tr": "Yasal uyarılar", "az": "Hüquqi xəbərdarlıqlar",
        "kk": "Заңдық ескертулер", "ky": "Мыйзамдуу эскертүүлөр",
        "uz": "Qonuniy ogohlantirishlar", "tk": "Kanun duýduryşlary",
        "tt": "Хокук искәрмәләре", "ba": "Хокуҡ иҫкәртеүҙәре",
    },
    "privacy": {
        "fr": "Confidentialité", "en": "Privacy", "it": "Privacy",
        "es": "Privacidad", "pt": "Privacidade", "ar": "الخصوصية",
        "tr": "Gizlilik", "az": "Gizlilik", "kk": "Құпиялық", "ky": "Купуялык",
        "uz": "Maxfiylik", "tk": "Gizlinlik", "tt": "Хосусыйлык", "ba": "Йәшерenлек",
    },
    "license": {
        "fr": "Licence", "en": "License", "it": "Licenza", "es": "Licencia",
        "pt": "Licença", "ar": "الترخيص", "tr": "Lisans", "az": "Lisenziya",
        "kk": "Лицензия", "ky": "Лицензия", "uz": "Litsenziya", "tk": "Lisenzia",
        "tt": "Лицензия", "ba": "Лисензия",
    },
}

LANG_LABELS = {
    "fr": "Français", "ar": "العربية", "en": "English", "it": "Italiano",
    "es": "Español", "pt": "Português", "tr": "Türkçe", "az": "Azərbaycanca",
    "kk": "Қазақша", "ky": "Кыргызча", "uz": "Oʻzbekcha", "tk": "Türkmençe",
    "tt": "Татарча", "ba": "Башҡортса",
}


def pick_lang(cookie_value: str | None, accept_language: str | None) -> str:
    """Cookie `lang` prioritaire, sinon en-tête Accept-Language."""
    if cookie_value:
        return normalize(cookie_value)
    if accept_language:
        for part in accept_language.split(","):
            code = part.split(";")[0].strip()
            g = code.lower().split("-")[0]
            if g in LANG_LABELS:
                return g
    return DEFAULT_LANG


def normalize(lang: str | None) -> str:
    """Normalise un code BCP47 (tr-AZ, pt-BR...) vers une clé supportée."""
    if not lang:
        return DEFAULT_LANG
    g = lang.lower().split("-")[0]
    if g in LANG_LABELS:
        return g
    if g in ("sah", "cv", "gag"):     # autres langues turciques -> turc
        return "tr"
    return "en"                       # tout le reste -> anglais (fallback neutre)


# ---------------------------------------------------------------------------
# Deuxieme bloc de cles : page Parametres + pages legales.
# Filtre anti-repli : toute cle deja presente dans MESSAGES est ignoree ici.
# Source de verite : app/i18n_data/messages.json (genere, complet, 14 langues).
# ---------------------------------------------------------------------------
MESSAGES.update({k: v for k, v in {
    "nav_settings": {"fr": "Paramètres", "en": "Settings", "it": "Impostazioni",
        "es": "Ajustes", "pt": "Configurações", "ar": "الإعدادات", "tr": "Ayarlar",
        "az": "Ayarlar", "kk": "Параметрлер", "ky": "Параметрлер", "uz": "Sozlamalar",
        "tk": "Sazlamalar", "tt": "Көйләүләр", "ba": "Көйләүҙәр"},
    "settings_general": {"fr": "Réglages généraux", "en": "General settings",
        "it": "Impostazioni generali", "es": "Ajustes generales", "pt": "Configurações gerais",
        "ar": "الإعدادات العامة", "tr": "Genel ayarlar", "az": "Ümumi ayarlar",
        "kk": "Жалпы параметрлер", "ky": "Жалпы параметрлер", "uz": "Umumiy sozlamalar",
        "tk": "Umumy sazlamalar", "tt": "Гомуми көйләүләр", "ba": "Дөйөм көйләүҙәр"},
    "settings_legal": {"fr": "Informations légales (éditeur)", "en": "Legal information (editor)",
        "it": "Informazioni legali (editore)", "es": "Información legal (editor)",
        "pt": "Informações legais (editor)", "ar": "المعلومات القانونية (الناشر)",
        "tr": "Yasal bilgiler (yayıncı)", "az": "Hüquqi məlumatlar (nəşriyyatçı)",
        "kk": "Заңдық ақпарат (баспа)", "ky": "Мыйзамдуу маалымат (басма)",
        "uz": "Qonuniy maʼlumot (noshir)", "tk": "Kanun maglumaty (neşirçi)",
        "tt": "Хокукый мәгълүмат (нәшерләүче)", "ba": "Хоҡуҡи мәғлүмәт (нәшриәтсе)"},
    "set_app_name": {"fr": "Nom de l'application", "en": "Application name",
        "it": "Nome applicazione", "es": "Nombre de la aplicación", "pt": "Nome do aplicativo",
        "ar": "اسم التطبيق", "tr": "Uygulama adı", "az": "Tətbiq adı",
        "kk": "Қосымша атауы", "ky": "Тиркеме аталышы", "uz": "Ilova nomi",
        "tk": "Programma ady", "tt": "Кушымта исеме", "ba": "Ҡушымта исеме"},
    "set_language": {"fr": "Langue", "en": "Language", "it": "Lingua", "es": "Idioma",
        "pt": "Idioma", "ar": "اللغة", "tr": "Dil", "az": "Dil", "kk": "Тіл",
        "ky": "Тил", "uz": "Til", "tk": "Dil", "tt": "Тел", "ba": "Тел"},
    "set_tolerance": {"fr": "Tolérance d'arrondi par défaut (€)", "en": "Default rounding tolerance (€)",
        "it": "Tolleranza di arrotondamento predefinita (€)", "es": "Tolerancia de redondeo predeterminada (€)",
        "pt": "Tolerância de arredondamento padrão (€)", "ar": "تسامح التقريب الافتراضي (يورو)",
        "tr": "Varsayılan yuvarlama toleransı (€)", "az": "Defay yuvarlama tolerantlığı (€)",
        "kk": "Әдепкі дөңгелектеу төзімділігі (€)", "ky": "Демейки тегеректөө чыдамдуулугу (€)",
        "uz": "Standart yaxlitlash chidamliligi (€)", "tk": "Standart tegekleme çydamlylygy (€)",
        "tt": "Стандарт түгәрәкләү допусгы (€)", "ba": "Стандарт түгәрәкләү допустһы (€)"},
    "set_currency": {"fr": "Devise", "en": "Currency", "it": "Valuta", "es": "Moneda",
        "pt": "Moeda", "ar": "العملة", "tr": "Para birimi", "az": "Valyuta",
        "kk": "Валюта", "ky": "Валюта", "uz": "Valyuta", "tk": "Walýuta",
        "tt": "Валюта", "ba": "Валюта"},
    "set_editor_name": {"fr": "Éditeur (affiché dans les mentions légales)", "en": "Editor name (shown in legal notice)",
        "it": "Nome editore (nota legale)", "es": "Editor (aviso legal)", "pt": "Editor (aviso legal)",
        "ar": "الناشر (في الإشعار القانوني)", "tr": "Yayıncı adı (yasal uyarılarda)",
        "az": "Nəşriyyatçı adı", "kk": "Баспа атауы", "ky": "Басма аталышы",
        "uz": "Noshir nomi", "tk": "Neşirçiniň ady", "tt": "Нәшерләүче исеме", "ba": "Нәшриәтсе исеме"},
    "set_editor_email": {"fr": "E-mail de contact légal", "en": "Legal contact e-mail",
        "it": "E-mail di contatto legale", "es": "Correo de contacto legal",
        "pt": "E-mail de contato legal", "ar": "بريد الاتصال القانوني",
        "tr": "Yasal iletişim e-postası", "az": "Hüquqi əlaqə e-poçtu",
        "kk": "Заңдық байланыс э-поштасы", "ky": "Мыйзамдуу байланыш э-почтасы",
        "uz": "Qonuniy aloqa elektron pochtasi", "tk": "Kanun aragatnaşyk e-pohtasy",
        "tt": "Хокукый элемтә электрон почтасы", "ba": "Хоҡуҡи бәйләнеш электрон почтаһы"},
    "save": {"fr": "Enregistrer", "en": "Save", "it": "Salva", "es": "Guardar",
        "pt": "Salvar", "ar": "حفظ", "tr": "Kaydet", "az": "Yadda saxla",
        "kk": "Сақтау", "ky": "Сактоо", "uz": "Saqlash", "tk": "Ýatda sakla",
        "tt": "Саклау", "ba": "Һаҡлау"},
    "settings_hint": {"fr": "Ces réglages sont stockés localement dans votre base SQLite ; ils priment sur les variables d'environnement. La tolérance reste personnalisable par fournisseur.",
        "en": "These settings are stored locally in your SQLite database; they override environment variables. Per-supplier tolerance still applies.",
        "tr": "Bu ayarlar yerel SQLite veritabanında saklanır ve ortam değişkenlerinin önüne geçer.",
        "ar": "تُخزَّن هذه الإعدادات محليًا في قاعدة SQLite الخاصة بك، وتأخذ الأولوية على متغيرات البيئة."},
    "settings_legal_hint": {"fr": "Utilisés dans les mentions légales, la politique de confidentialité et les exports. Conformité art. 6 LCEN (France) et RGPD.",
        "en": "Used in the legal notice, privacy policy and exports. Complies with French LCEN art. 6 and GDPR.",
        "tr": "Yasal uyarılar, gizlilik politikası ve dışa aktarımlarda kullanılır.",
        "ar": "تُستخدم في الإشعارات القانونية وسياسة الخصوصية والملفات المصدَّرة."},
    "legal_title": {"fr": "Mentions légales & déclarations", "en": "Legal notice & disclaimers",
        "it": "Note legali e dichiarazioni", "es": "Aviso legal y declaraciones",
        "pt": "Avisos legais e declarações", "ar": "الإشعارات القانونية والإقرارات",
        "tr": "Yasal uyarılar ve beyanlar", "az": "Hüquqi xəbərdarlıqlar və bəyanatlar",
        "kk": "Заңдық ескертулер мен мәлімдемeler", "ky": "Мыйзамдуу эскертүүлөр жана билдирүүлөр",
        "uz": "Qonuniy ogohlantirishlar va bayonotlar", "tk": "Kanun duýduryşlary we beýanlary",
        "tt": "Хокук искәрмәләре һәм белдерүләр", "ba": "Хоҡуҡ иҫкәртеүҙәр һәм белдереүҙәр"},
    "legal_editor": {"fr": "Éditeur du logiciel", "en": "Software publisher", "it": "Editore del software",
        "es": "Editor del software", "pt": "Publicador do software", "ar": "ناشر البرنامج",
        "tr": "Yazılım yayıncısı", "az": "Proqram nəşriyyatçısı", "kk": "Бағдарлама баспасы",
        "ky": "Программа басмасы", "uz": "Dastur noshiri", "tk": "Programma neşirçisi",
        "tt": "Программаны нәшерләүче", "ba": "Программаны нәшриәтсеһе"},
    "legal_object": {"fr": "Objet de l'application", "en": "Purpose of the application",
        "it": "Scopo dell'applicazione", "es": "Objeto de la aplicación", "pt": "Objetivo do aplicativo",
        "ar": "غرض التطبيق", "tr": "Uygulamanın amacı", "az": "Tətbiqin məqsədi",
        "kk": "Қосымшаның мақсаты", "ky": "Тиркеменин максаты", "uz": "Ilovaning maqsadi",
        "tk": "Programmanyň maksady", "tt": "Кушымтаның максаты", "ba": "Ҡушымтаның маҡсаты"},
    "legal_ip": {"fr": "Propriété intellectuelle", "en": "Intellectual property",
        "it": "Proprietà intellettuale", "es": "Propiedad intelectual", "pt": "Propriedade intelectual",
        "ar": "الملكية الفكرية", "tr": "Fikri mülkiyet", "az": "Əqli mülkiyyət",
        "kk": "Зияткерлік меншік", "ky": "Интеллектуалдык менчик", "uz": "Intellektual mulk",
        "tk": "Zehin eýeçiligi", "tt": "Интеллектуаль милек", "ba": "Интеллектуаль милек"},
    "legal_warranty": {"fr": "Garantie & exactitude des calculs", "en": "Warranty & calculation accuracy",
        "it": "Garanzia ed esattezza dei calcoli", "es": "Garantía y exactitud de los cálculos",
        "pt": "Garantia e exatidão dos cálculos", "ar": "الضمان ودقة الحسابات",
        "tr": "Taahhüt ve hesap doğruluğu", "az": "Zəmanət və hesabat dəqiqliyi",
        "kk": "Кепілдік және есеп дәлдігі", "ky": "Кепилдик жана эсеп тактыгы",
        "uz": "Kafolat va hisob aniqligi", "tk": "Kepil we hasap takkalygy",
        "tt": "Кепләү һәм исәпләү төгәллеге", "ba": "Кепләү һәм иҫәпләү төгәллеге"},
    "legal_liability": {"fr": "Limitation de responsabilité", "en": "Limitation of liability",
        "it": "Limitazione di responsabilità", "es": "Limitación de responsabilidad",
        "pt": "Limitação de responsabilidade", "ar": "حدود المسؤولية",
        "tr": "Sorumluluk sınırlaması", "az": "Məsuliyyətin məhdudlaşdırılması",
        "kk": "Жауапкершілікті шектеу", "ky": "Жоопкерчиликти чектөө",
        "uz": "Mas'uliyatni cheklash", "tk": "Jogapkärçiligi çäklendirmek",
        "tt": "Җаваплылыкны чикләү", "ba": "Яуаплылыҡты сиклеү"},
    "legal_cookies": {"fr": "Cookies", "en": "Cookies", "it": "Cookie", "es": "Cookies",
        "pt": "Cookies", "ar": "ملفات تعريف الارتباط", "tr": "Çerezler", "az": "Cookilər",
        "kk": "Cookie файлдары", "ky": "Cookie файлдары", "uz": "Cookie fayllari",
        "tk": "Cookie faýllary", "tt": "Cookie файллары", "ba": "Cookie файлдары"},
    "legal_einvoice": {"fr": "Facture électronique (conformité)", "en": "Electronic invoicing (compliance)",
        "it": "Fatturazione elettronica (conformità)", "es": "Facturación electrónica (cumplimiento)",
        "pt": "Faturação eletrónica (conformidade)", "ar": "الفوترة الإلكترونية (الامتثال)",
        "tr": "Elektronik fatura (uyumluluk)", "az": "Elektron faktura (uyğunluq)",
        "kk": "Электрон шот-фактура (сәйкестік)", "ky": "Электрон эсеп-фактура (шайкештик)",
        "uz": "Elektron hisob-faktura (moslik)", "tk": "Elektron hasap-faktura (laýyklyk)",
        "tt": "Электрон фактура (туры килү)", "ba": "Электрон фактура (ярау)"},
    "legal_applicable": {"fr": "Droit applicable", "en": "Applicable law", "it": "Legge applicabile",
        "es": "Legislación aplicable", "pt": "Legislação aplicável", "ar": "القانون الواجب التطبيق",
        "tr": "Geçerli hukuk", "az": "Tətbiq olunan hüquq", "kk": "Қолданылатын заң",
        "ky": "Колдонулуучу мыйзам", "uz": "Qoʻllaniladigan qonun", "tk": "Ulanylýan kanun",
        "tt": "Кулланыла торган закон", "ba": "Ҡулланылған закон"},
    "privacy_title": {"fr": "Politique de confidentialité", "en": "Privacy policy",
        "it": "Informativa sulla privacy", "es": "Política de privacidad",
        "pt": "Política de privacidade", "ar": "سياسة الخصوصية", "tr": "Gizlilik politikası",
        "az": "Gizlilik siyasəti", "kk": "Құпиялық саясаты", "ky": "Купуялык саясаты",
        "uz": "Maxfiylik siyosati", "tk": "Gizlinlik syýasaty", "tt": "Хосусыйлык сәясәте",
        "ba": "Йәшеренлек сәйәсәте"},
    "license_title": {"fr": "Licence d'utilisation", "en": "Usage license", "it": "Licenza d'uso",
        "es": "Licencia de uso", "pt": "Licença de uso", "ar": "ترخيص الاستخدام",
        "tr": "Kullanım lisansı", "az": "İstifadə lisenziyası", "kk": "Пайдалану лицензиясы",
        "ky": "Колдонуу лицензиясы", "uz": "Foydalanish litsenziyasi", "tk": "Ulanyş lisenziýasy",
        "tt": "Куллану лицензиясе", "ba": "Файҙланыу лисензияһы"},
    "disclaimer_title": {"fr": "Disclaimer", "en": "Disclaimer", "it": "Avvertenze",
        "es": "Descargo de responsabilidad", "pt": "Aviso legal", "ar": "إخلاء المسؤولية",
        "tr": "Sorumluluk reddi", "az": "Məsuliyyətdən imtina", "kk": "Ескерту",
        "ky": "Эскертүү", "uz": "Ogohlantirish", "tk": "Duýduryş", "tt": "Искәрмә", "ba": "Иҫкәртеү"},
    "lb_edited_by": {"fr": "Ce logiciel est édité par {name}.", "en": "This software is published by {name}.",
        "it": "Questo software è pubblicato da {name}.", "es": "Este software es publicado por {name}.",
        "pt": "Este software é publicado por {name}.", "ar": "هذا البرنامج منشور من قِبل {name}.",
        "tr": "Bu yazılımın yayıncısı: {name}.", "az": "Bu proqramın nəşriyyatçısı: {name}.",
        "kk": "Бұл бағдарламаның баспасы: {name}.", "ky": "Бул программанын басмасы: {name}.",
        "uz": "Ushbu dasturning noshiri: {name}.", "tk": "Bu programmanyň neşirçisi: {name}.",
        "tt": "Бу программаны нәшерләүче: {name}.", "ba": "Бы programmaһын нәшриәтсеһе: {name}."},
    "lb_contact": {"fr": "Contact : {email}", "en": "Contact: {email}", "it": "Contatto: {email}",
        "es": "Contacto: {email}", "pt": "Contato: {email}", "ar": "اتصل بنا: {email}",
        "tr": "İletişim: {email}", "az": "Əlaqə: {email}", "kk": "Байланыс: {email}",
        "ky": "Байланыш: {email}", "uz": "Aloqa: {email}", "tk": "Aragatnaşyk: {email}",
        "tt": "Элемтә: {email}", "ba": "Бәйләнеш: {email}"},
    "lb_hosting": {"fr": "Le logiciel s'exécute intégralement sur votre propre machine (auto-hébergement : PC, serveur, NAS ou Raspberry Pi). Aucune donnée n'est hébergée chez un tiers.",
        "en": "The software runs entirely on your own machine (self-hosted: PC, server, NAS or Raspberry Pi). No data is hosted by any third party.",
        "tr": "Yazılım tamamen kendi cihazınızda çalışır (PC, sunucu, NAS veya Raspberry Pi). Üçüncü tarafta veri barındırılmaz.",
        "ar": "يعمل البرنامج بالكامل على جهازك الخاص (استضافة ذاتية: حاسوب، خادم، NAS أو راسبيري باي). لا تُستضاف أي بيانات لدى طرف ثالث."},
    "lb_object": {"fr": "Doğruluk vérifie les devis et factures fournisseurs ligne à ligne contre vos listes de prix négociées, calcule les écarts ((prix facturé − prix convenu) × quantité), met de côté les articles sans prix de référence (« je n'ai pas le prix de ça ») et produit un récapitulatif des achats par chantier. Il lit Excel/CSV, PDF, Factur-X, UBL et CII.",
        "en": "Doğruluk checks supplier quotes and invoices line by line against your negotiated price lists, computes discrepancies ((billed price − agreed price) × quantity), sets aside items without a reference price and produces a per-job-site purchase summary. It reads Excel/CSV, PDF, Factur-X, UBL and CII.",
        "tr": "Doğruluk, tedarikçi tekliflerini ve faturalarını pazarlık edilmiş fiyat listelerinize göre satır satır denetler, farkları ((fatura fiyatı − anlaşmalı fiyat) × miktar) hesaplar ve şantiye bazlı özet üretir. Excel/CSV, PDF, Factur-X, UBL ve CII okur.",
        "ar": "يتحقق Doğruluk من عروض الموردين وفواتيرهم سطرًا بسطر مقابل قوائم الأسعار المتفق عليها، ويحسب الفروقات ويجنّب الأصناف التي لا سعر مرجعي لها، وينتج ملخصًا للمشتريات حسب ورشة العمل."},
    "lb_ip": {"fr": "Le code source, la marque « Doğruluk » et les documents associés sont la propriété de {name} ({year}), distribués sous licence {license}. Toute reproduction non autorisée constitue une contrefaçon.",
        "en": "The source code, the “Doğruluk” trademark and associated documents are the property of {name} ({year}), distributed under the {license} licence. Any unauthorised reproduction constitutes infringement.",
        "tr": "Kaynak kodu, “Doğruluk” markası ve ilgili belgeler {name} aittir ({year}) ve {license} lisansısıyla dağıtılır.",
        "ar": "الكود المصدري وعلامة «Doğruluk» والوثائق المرتبطة مملوكة لـ {name} ({year}) وموزَّعة بموجب رخصة {license}."},
    "lb_warranty": {"fr": "Doğruluk est fourni « en l'état », sans garantie explicite ou implicite de résultat. Les contrôles de prix sont indicatifs : toute réclamation (avoir, remboursement) doit être validée par vos propres vérifications contractuelles avant envoi au fournisseur.",
        "en": "Doğruluk is provided “as is”, without any explicit or implied warranty. Price checks are indicative: any claim (credit note, refund) must be validated by your own contractual review before being sent to the supplier.",
        "tr": "Doğruluk olduğu gibi sunulmaktadır; açık veya zımni bir sonuç garantisi verilmez. Fiyat kontrolleri yol göstericidir.",
        "ar": "يُقدَّم Doğruluk «كما هو» دون أي ضمان صريح أو ضمني. فحوص الأسعار إرشادية: يجب التحقق تعاقديًا قبل تقديم أي مطالبة للمورد."},
    "lb_no_legal_advice": {"fr": "⚠ Ce logiciel n'est pas un conseil juridique ou comptable. Pour tout litige fournisseur, consultez un professionnel.",
        "en": "⚠ This software does not provide legal or accounting advice. For any supplier dispute, consult a professional.",
        "tr": "⚠ Bu yazılım hukuki veya mali danışmanlık sağlamaz.",
        "ar": "⚠ هذا البرنامج لا يقدّم استشارات قانونية أو محاسبية."},
    "lb_liability": {"fr": "Dans les limites permises par la loi, l'éditeur ne peut être tenu responsable des dommages indirects (perte de données, perte financière, retard de réclamation) résultant de l'utilisation ou de l'impossibilité d'utiliser Doğruluk. Sauvegardez régulièrement votre dossier `data/`.",
        "en": "To the extent permitted by law, the publisher cannot be held liable for indirect damages (data loss, financial loss, late claims) arising from use or inability to use Doğruluk. Back up your `data/` folder regularly.",
        "tr": "Yasanın izin verdiği ölçüde yayıncı, dolaylı zararlardan sorumlu tutulamaz. `data/` klasörünü düzenli yedekleyin.",
        "ar": "في حدود ما يسمح به القانون، لا يمكن تحميل الناشر مسؤولية الأضرار غير المباشرة. قم بنسخ مجلد `data/` دوريًا."},
    "lb_privacy": {"fr": "Doğruluk est un logiciel local : aucune donnée personnelle ni commerciale n'est transmise sur Internet. Les prix, lignes de facture et noms de chantier restent dans votre base SQLite locale (`data/verif.db`).",
        "en": "Doğruluk is local software: no personal or business data is transmitted over the Internet. Prices, invoice lines and job-site names stay in your local SQLite database (`data/verif.db`).",
        "tr": "Doğruluk yerel bir yazılımdır; hiçbir veri İnternet'e gönderilmez.",
        "ar": "Doğruluk برنامج محلي: لا تُرسَل أي بيانات عبر الإنترنت."},
    "lb_data_local": {"fr": "Données traitées : fournisseurs, listes de prix, factures/devis, chantiers — uniquement sur votre machine.",
        "en": "Data processed: suppliers, price lists, invoices/quotes, job sites — only on your machine.",
        "tr": "İşlenen veriler: tedarikçiler, fiyat listeleri, faturalar, şantiyeler — yalnızca cihazınızda.",
        "ar": "البيانات المعالجة: الموردون وقوائم الأسعار والفواتير وورش العمل — على جهازك فقط."},
    "lb_data_none_sent": {"fr": "Aucune télémétrie, aucun cookie de suivi, aucune analyse tierce.",
        "en": "No telemetry, no tracking cookies, no third-party analytics.",
        "tr": "Telemetri, takip çerezi veya üçüncü taraf analitik yok.",
        "ar": "لا قياس عن بُعد ولا ملفات تتبع ولا تحليلات لطرف ثالث."},
    "lb_rgpd": {"fr": "Conformément au RGPD (UE 2016/679) et à la loi Informatique & Libertés, vous êtes responsable des données que vous importez ; leur suppression se fait en effaçant `data/verif.db`.",
        "en": "Under GDPR (EU 2016/679) and the French IT & Freedoms Act, you are responsible for the data you import; delete it by removing `data/verif.db`.",
        "tr": "GDPR kapsamında içe aktardığınız verilerin sorumlusu sizsiniz; silmek için `data/verif.db` dosyasını kaldırın.",
        "ar": "بموجب GDPR، أنت مسؤول عن البيانات التي تستوردها؛ احذفها بإزالة الملف `data/verif.db`."},
    "lb_cookies": {"fr": "Un seul cookie technique strictement nécessaire est utilisé : `lang` (préférence d'affichage de la langue). Il ne nécessite pas de consentement au sens de l'article 82 de la loi LCEN / directive ePrivacy.",
        "en": "A single strictly necessary technical cookie is used: `lang` (display language preference). No consent banner required under ePrivacy / LCEN art. 82.",
        "tr": "Yalnızca teknik bir çerez kullanılır: `lang`. Onay bildirimi gerekmez.",
        "ar": "يُستخدم ملف تعريف ارتباط تقني واحد فقط باسم `lang`، وهو لا يحتاج إلى موافقة."},
    "lb_einvoice": {"fr": "Doğruluk prend en charge la facture électronique française (Factur-X, UBL, CII) conformément à la réforme issue de la LFR 2024 (obligation de réception dès sept. 2026 pour toutes les entreprises assujetties à la TVA). Le logiciel ne remplace pas une plateforme de dématérialisation partenaire (PDP) agréée : il lit et contrôle les factures que vous recevez.",
        "en": "Doğruluk supports French e-invoicing formats (Factur-X, UBL, CII) under the 2024 finance act reform (reception mandatory from Sept. 2026 for all VAT-registered businesses). It is not a replacement for a certified PDP portal: it reads and audits the invoices you receive.",
        "tr": "Doğruluk Fransız e-fatura biçimlerini (Factur-X, UBL, CII) destekler; ancak onaylı bir PDP platformunun yerine geçmez.",
        "ar": "يدعم Doğruluk صيغ الفوترة الإلكترونية الفرنسية (Factur-X وUBL وCII) لكنه لا يحل محل منصة معتمدة (PDP)."},
    "lb_applicable": {"fr": "Les présentes conditions sont régies par le droit français. À défaut d'accord amiable, compétence est attribuée aux tribunaux du ressort de la Cour d'appel de Metz, France.",
        "en": "These terms are governed by French law. Failing an amicable agreement, the courts within the Metz Court of Appeals jurisdiction (France) have competence.",
        "tr": "Bu koşullar Fransız hukukuna tabidir.",
        "ar": "تخضع هذه الشروط للقانون الفرنسي."},
    "lb_license_intro": {"fr": "Doğruluk v{version} — Copyright © {year} {name}. Licence : {license}.",
        "en": "Doğruluk v{version} — Copyright © {year} {name}. License: {license}.",
        "tr": "Doğruluk v{version} — Telif hakkı © {year} {name}. Lisans: {license}.",
        "ar": "Doğruluk الإصدار {version} — حقوق النشر © {year} {name}. الترخيص: {license}."},
    "lb_license_body": {"fr": "Vous êtes autorisé à utiliser, copier et modifier ce logiciel pour vos besoins professionnels internes, à condition de conserver la mention de crédit « David HARPUTOGLU — aidé par IA ». La redistribution commerciale ou la revente du logiciel lui-même est interdite sans accord écrit préalable de l'éditeur. Les données que vous importez vous appartiennent.",
        "en": "You may use, copy and modify this software for your internal business needs, provided the credit notice “David HARPUTOGLU — aided by AI” is retained. Commercial redistribution or resale of the software itself requires prior written consent from the publisher. The data you import remains yours.",
        "tr": "Bu yazılımı iç iş ihtiyaçlarınız için kullanabilir, kopyalayabilir ve değiştirebilirsiniz; “David HARPUTOGLU — yapay zekâ desteğiyle” ibaresinin korunması şartıyla. Ticari yeniden dağıtım önceden yazılı izin gerektirir.",
        "ar": "يُسمح لك باستخدام هذا البرنامج ونسخه وتعديله لأغراضك المهنية الداخلية شريطة الاحتفاظ بعبارة النسبة «David HARPUTOGLU — بمساعدة الذكاء الاصطناعي». يُمنع إعادة التوزيع التجاري دون إذن كتابي مسبق."},
    "lb_disclaimer": {"fr": "« Point.P » est une marque déposée de ses propriétaires respectifs ; ce projet n'est affilié ni sponsorisé ni cautionné par Point.P ni par aucun autre fournisseur cité. Toutes les autres marques appartiennent à leurs titulaires.",
        "en": "“Point.P” is a registered trademark of its respective owners; this project is not affiliated with, sponsored or endorsed by Point.P or any other mentioned supplier. All other trademarks belong to their holders.",
        "tr": "“Point.P” ilgili sahiplerinin tescilli markasıdır; bu proje onunla bağlantılı değildir.",
        "ar": "«Point.P» علامة تجارية مسجلة لأصحابها؛ هذا المشروع غير تابع لها أو مدعوم منها."},
    "lb_last_update": {"fr": "Dernière mise à jour : {date}", "en": "Last updated: {date}",
        "it": "Ultimo aggiornamento: {date}", "es": "Última actualización: {date}",
        "pt": "Última atualização: {date}", "ar": "آخر تحديث: {date}",
        "tr": "Son güncelleme: {date}", "az": "Son yeniləmə: {date}", "kk": "Соңғы жаңарту: {date}",
        "ky": "Акыркы жаңыртуу: {date}", "uz": "Oxirgi yangilanish: {date}",
        "tk": "Soňky täzelenme: {date}", "tt": "Ахыргы яңарту: {date}", "ba": "Ахыргы яңартыу: {date}"},
    # ---- thèmes d'interface ----
    "theme_dark": {"fr": "Sombre", "en": "Dark", "it": "Scuro", "es": "Oscuro",
        "pt": "Escuro", "ar": "داكن", "tr": "Koyu", "az": "Qaranlıq",
        "kk": "Күңгірт", "ky": "Караңгы", "uz": "Tungi", "tk": "Garaňky",
        "tt": "Караңгы", "ba": "Ҡараңғы"},
    "theme_black": {"fr": "Noir", "en": "Black", "it": "Nero", "es": "Negro",
        "pt": "Preto", "ar": "أسود", "tr": "Siyah", "az": "Qara",
        "kk": "Қара", "ky": "Кара", "uz": "Qora", "tk": "Gara",
        "tt": "Кара", "ba": "Ҡара"},
    "theme_custom": {"fr": "Personnalisé", "en": "Custom", "it": "Personalizzato",
        "es": "Personalizado", "pt": "Personalizado", "ar": "مخصص",
        "tr": "Özel", "az": "Fərdi", "kk": "Арнайы", "ky": "Өнөктөш",
        "uz": "Maxsus", "tk": "Ýörite", "tt": "Үзгәртеп", "ba": "Үҙгәртелгән"},
    "theme_custom_primary": {"fr": "Couleur principale", "en": "Primary color",
        "it": "Colore principale", "es": "Color principal", "pt": "Cor principal",
        "ar": "اللون الرئيسي", "tr": "Ana renk", "az": "Əsas rəng",
        "kk": "Негізгі түс", "ky": "Негизги түс", "uz": "Asosiy rang",
        "tk": "Esasy reňk", "tt": "Төп төс", "ba": "Төҫ төҫө"},
    "theme_custom_secondary": {"fr": "Couleur secondaire", "en": "Secondary color",
        "it": "Colore secondario", "es": "Color secundario", "pt": "Cor secundária",
        "ar": "اللون الثانوي", "tr": "İkincil renk", "az": "İkinci rəng",
        "kk": "Екінші түс", "ky": "Экинчи түс", "uz": "Ikkilamchi rang",
        "tk": "Ikinji reňk", "tt": "Икенче төс", "ba": "Икенсе төҫ"},
}.items() if k not in MESSAGES})


def translate(key: str, lang: str, params: dict | None = None) -> str:
    entry = MESSAGES.get(key)
    text = (entry.get(lang) or entry.get("en") or key) if entry else key
    if params:
        for k, v in params.items():
            text = text.replace("{" + k + "}", str(v))
    return text


def tr_ctx(lang: str):
    """Retourne la fonction t(cle, params=None) liee a une langue (pour Jinja)."""
    return lambda key, params=None: translate(key, lang, params)
