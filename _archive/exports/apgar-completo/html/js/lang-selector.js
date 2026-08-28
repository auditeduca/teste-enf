/* ======================================================================
   lang-selector.js — Seletor de idiomas com bandeiras (30 idiomas)
   Calculadoras de Enfermagem — Global Platform
   Popula os dropdowns do cabeçalho (#rd-lang-*) e do rodapé (#rd-lang-*-2),
   aplica traduções aos elementos [data-i18n] / [data-i18n-placeholder] e
   persiste a escolha do usuário em localStorage.
   ====================================================================== */

(function () {
  var FLAG_DIR = "images/flags/";

  var LANGUAGES = [
    { code: "pt-BR", native: "Português (Brasil)", short: "PT", flag: "br.webp" },
    { code: "en",    native: "English",             short: "EN", flag: "us.webp" },
    { code: "es",    native: "Español",             short: "ES", flag: "es.webp" },
    { code: "fr",    native: "Français",            short: "FR", flag: "fr.webp" },
    { code: "de",    native: "Deutsch",              short: "DE", flag: "de.webp" },
    { code: "it",    native: "Italiano",             short: "IT", flag: "it.webp" },
    { code: "nl",    native: "Nederlands",           short: "NL", flag: "nl.webp" },
    { code: "pl",    native: "Polski",               short: "PL", flag: "pl.webp" },
    { code: "ru",    native: "Русский",              short: "RU", flag: "ru.webp" },
    { code: "tr",    native: "Türkçe",               short: "TR", flag: "tr.webp" },
    { code: "ar",    native: "العربية",              short: "AR", flag: "sa.webp" },
    { code: "he",    native: "עברית",                short: "HE", flag: "il.webp" },
    { code: "hi",    native: "हिन्दी",                short: "HI", flag: "in.webp" },
    { code: "bn",    native: "বাংলা",                 short: "BN", flag: "bd.webp" },
    { code: "zh-CN", native: "中文（简体）",           short: "ZH", flag: "cn.webp" },
    { code: "zh-TW", native: "中文（繁體）",           short: "ZH", flag: "tw.webp" },
    { code: "ja",    native: "日本語",                short: "JA", flag: "jp.webp" },
    { code: "ko",    native: "한국어",                short: "KO", flag: "kr.webp" },
    { code: "vi",    native: "Tiếng Việt",           short: "VI", flag: "vn.webp" },
    { code: "th",    native: "ไทย",                  short: "TH", flag: "th.webp" },
    { code: "id",    native: "Bahasa Indonesia",     short: "ID", flag: "id.webp" },
    { code: "ms",    native: "Bahasa Melayu",        short: "MS", flag: "my.webp" },
    { code: "tl",    native: "Filipino",             short: "TL", flag: "ph.webp" },
    { code: "sw",    native: "Kiswahili",            short: "SW", flag: "ke.webp" },
    { code: "am",    native: "አማርኛ",                 short: "AM", flag: "et.webp" },
    { code: "el",    native: "Ελληνικά",             short: "EL", flag: "gr.webp" },
    { code: "ro",    native: "Română",               short: "RO", flag: "ro.webp" },
    { code: "hu",    native: "Magyar",               short: "HU", flag: "hu.webp" },
    { code: "cs",    native: "Čeština",              short: "CS", flag: "cz.webp" },
    { code: "sv",    native: "Svenska",              short: "SV", flag: "se.webp" }
  ];

  var TRANSLATIONS = {
    en: {
      "nav.inicio": "Home", "nav.assistencia": "Care", "nav.educacao": "Education",
      "nav.faleconosco": "Contact", "nav.pesquisa": "Search", "nav.idiomas": "Languages", "nav.ferramentas": "Tools",
      "nav.gestao": "Management", "nav.recursos": "Resources", "nav.institucional": "Institutional",
      "nav.entrar": "Log in", "nav.criar": "Create account",
      "aria.busca": "Open search", "aria.idiomas": "Select language", "aria.idiomasDropdown": "Language selector",
      "aria.menu": "Open menu", "aria.navPrincipal": "Main navigation", "aria.buscarInput": "Search the site",
      "aria.mobileMenu": "Mobile menu",
      "busca.titulo": "Search the site", "busca.placeholder": "Type what you're looking for...",
      "busca.btn": "Search", "busca.populares": "Popular searches",
      "idiomas.regiao": "Region", "idiomas.paises": "Countries in this region",
      "mega.subPrincipais": "Main sub-menus", "mega.demaisNav": "More navigation",
      "contact.sobre": "About the platform", "contact.ajuda": "Help Center",
      "mobile.buscarPh": "Search...",
      "content.avaliar": "Rate this content", "content.leitura": "Listen", "content.compartilhar": "Share",
      "content.salvar": "Save", "content.imprimir": "Print",
      "aria.fechar": "Close", "aria.fonteDec": "Decrease font size", "aria.fonteInc": "Increase font size",
      "aria.star5": "5 stars", "aria.star4": "4 stars", "aria.star3": "3 stars", "aria.star2": "2 stars", "aria.star1": "1 star",
      "a11y.tituloModal": "Accessibility preferences",
      "a11y.introModal": "Adjust the site display to your preference. Your choices are saved in this browser.",
      "a11y.fonteTitulo": "Font size", "a11y.fonteDesc": "Increase or decrease the text size across the site.",
      "a11y.contrasteTitulo": "High contrast", "a11y.contrasteDesc": "Increases color contrast for better readability.",
      "a11y.temaTitulo": "Dark mode", "a11y.temaDesc": "Switches the display to a dark background theme.",
      "a11y.dislexiaTitulo": "Dyslexia-friendly font", "a11y.dislexiaDesc": "Replaces the typography with an easier-to-read font.",
      "a11y.redefinir": "Reset all", "a11y.atalhos": "Keyboard shortcuts",
      "a11y.atalhosTitulo": "Keyboard shortcuts",
      "a11y.atalho1": "Navigate between elements", "a11y.atalho2": "Close menus, modals and the mobile menu",
      "a11y.atalho3": "Activate buttons and links", "a11y.atalho4": "Move between menu items",
      "cookie.aviso": "Cookie notice",
      "cookie.bannerText": '<strong>We use cookies.</strong> We use essential cookies and, with your consent, performance and personalization cookies to improve your experience. Learn more in our <a href="#">Privacy Policy</a>.',
      "cookie.personalizar": "Customize", "cookie.rejeitar": "Reject non-essential", "cookie.aceitar": "Accept all",
      "cookie.modalTitulo": "Cookie preferences",
      "cookie.modalIntro": "Choose which categories of cookies you allow. Essential cookies cannot be disabled as they are required for the platform to function.",
      "cookie.essenciaisTitulo": "Essential", "cookie.essenciaisDesc": "Required for login, security and basic platform functionality.",
      "cookie.desempenhoTitulo": "Performance", "cookie.desempenhoDesc": "Help us understand how visitors use the platform so we can continuously improve it.",
      "cookie.funcionalidadeTitulo": "Functionality", "cookie.funcionalidadeDesc": "Remember preferences such as language, region and font size.",
      "cookie.analiseTitulo": "Analytics & Advertising", "cookie.analiseDesc": "Used in aggregate to understand platform usage trends.",
      "cookie.salvar": "Save preferences",
      "herosearch.titulo": "What do you need today?",
      "herosearch.placeholder": "E.g.: Drip rate, Braden Scale, Insulin, NCP...",
      "seo.h1": "Nursing Calculators, Practice Exams and Clinical Scales",
      "seo.desc": "A complete platform with nursing calculators, clinical scales, medication dosage calculations and practice exams for public exams. Ideal for students, technicians and nurses who want to optimize daily practice, strengthen patient safety and prepare for exams.",
      "sol.eyebrow": "About the platform",
      "sol.titulo": "Solutions for every moment of your practice",
      "sol.desc": "Clinical tools, protocols, scales and educational content for students, nurses, managers and healthcare institutions — with digital accountability and measurable impact.",
      "sol.card1.titulo": "Global Reach", "sol.card1.desc": "Translated into more than 18 languages, covering over 140 countries.",
      "sol.card2.titulo": "Clinical Scales", "sol.card2.desc": "Over 60 automated clinical and care scales.",
      "sol.card3.titulo": "Calculators", "sol.card3.desc": "Over 15 care calculators to solve everyday calculations in the profession.",
      "sol.card4.titulo": "Practice Exams", "sol.card4.desc": "Interactive practice exams from leading exam boards, organized by topic with time and score tracking.",
      "sol.card5.titulo": "Library", "sol.card5.desc": "A growing collection serving as an exclusive base of nursing literature content.",
      "sol.card6.titulo": "Teaching", "sol.card6.desc": "A commitment to education through the development of exclusive literary content.",
      "sol.card7.titulo": "Accountability", "sol.card7.desc": "Credit to literature and use of bibliographic references to guide scales and content.",
      "sol.card8.titulo": "Security and Privacy", "sol.card8.desc": "Information protection and data governance across all platform tools.",
      "quick.eyebrow": "Quick access", "quick.titulo": "Most used tools", "quick.desc": "Access validated calculators and resources that make your daily routine easier.",
      "quick.link": "See all tools",
      "quick.card1": "Medication Calculation", "quick.card2": "IV Drip Rate", "quick.card3": "Indexes & Scales", "quick.card4": "Fluid Balance",
      "quick.card5": "Laboratory Tests", "quick.card6": "Insulin Calculation", "quick.card7": "BMI Calculation", "quick.card8": "All Tools",
      "edu.eyebrow": "Education", "edu.titulo": "Education that transforms", "edu.desc": "Up-to-date, evidence-based content developed by experts.",
      "edu.list1": "Nursing exam library", "edu.list2": "Interactive question quiz", "edu.list3": "Practice exams by board and institution", "edu.list4": "Nursing Diagnoses — NANDA",
      "edu.btn": "Access content",
      "gestao.eyebrow": "Management", "gestao.titulo": "Management that makes an impact", "gestao.desc": "Resources and indicators to support healthcare leaders and institutions.",
      "gestao.list1": "Nursing team staffing", "gestao.list2": "Fugulin Scale — care complexity", "gestao.list3": "Patient classification — Perroca (SCP)", "gestao.list4": "SBAR — shift handover",
      "gestao.btn": "Explore solutions",
      "cat.calc.eyebrow": "Support tools", "cat.calc.titulo": "Calculators — Practical Nursing",
      "tool.balancohidrico.titulo": "Calculate Fluid Balance", "tool.balancohidrico.desc": "Precise fluid control.",
      "tool.dimensionamento.titulo": "Nursing Staffing Calculator", "tool.dimensionamento.desc": "Organize your nursing team.",
      "tool.exames_laboratoriais.titulo": "Laboratory Test Calculator", "tool.exames_laboratoriais.desc": "Calculate laboratory test results.",
      "tool.gasometria.titulo": "Arterial Blood Gas Calculator", "tool.gasometria.desc": "Arterial blood gas interpretation.",
      "tool.gotejamento.titulo": "IV Drip Rate Calculator", "tool.gotejamento.desc": "Calculate the infusion rate.",
      "tool.gestacional.titulo": "Gestational Age & Due Date", "tool.gestacional.desc": "Calculate gestational age and estimated due date.",
      "tool.imc.titulo": "BMI Calculation", "tool.imc.desc": "Body Mass Index.",
      "tool.insulina.titulo": "Insulin Calculation", "tool.insulina.desc": "Insulin dose calculation.",
      "tool.medicamentos.titulo": "Medication Calculation", "tool.medicamentos.desc": "Drug doses and dilutions.",
      "tool.calculadoravacina.titulo": "Children's Vaccines", "tool.calculadoravacina.desc": "Automated vaccine schedule.",
      "tool.notificacao-compulsoria.titulo": "Notifiable Diseases", "tool.notificacao-compulsoria.desc": "Interactive list of the Ministry of Health's notifiable diseases and conditions.",
      "tool.diagnosticosnanda.titulo": "Nursing Diagnoses - NANDA", "tool.diagnosticosnanda.desc": "List of nursing diagnoses - NANDA (2018).",
      "tool.sbar.titulo": "SBAR - Shift Handover Form", "tool.sbar.desc": "Digital SBAR form for nurses — fill in and print.",
      "tool.calculo-de-ferias.titulo": "Vacation Pay Calculator (Nursing)", "tool.calculo-de-ferias.desc": "How much will you receive for vacation?",
      "tool.adicional-noturno.titulo": "Night Shift Differential Calculator (Nursing)", "tool.adicional-noturno.desc": "Calculate the value of your night shift differential.",
      "tool.calculo-hora-extra.titulo": "Overtime Pay Calculator (Nursing)", "tool.calculo-hora-extra.desc": "Calculate the value of your overtime pay.",
      "tool.calculo-rescisao.titulo": "Severance Pay Calculator (Nursing)", "tool.calculo-rescisao.desc": "Calculate the value of your contract termination settlement.",
      "cat.sim.eyebrow": "Exam Prep", "cat.sim.titulo": "Nursing Practice Exams — Boards & Institutions",
      "tool.simulado-de-enfermagem.titulo": "1st Practice Exam for Nursing Technicians", "tool.simulado-de-enfermagem.desc": "50 questions from leading exam boards and institutions, with a timer and final percentage score.",
      "tool.simulado-de-enfermagem4.titulo": "2nd (New) Practice Exam for Nursing Technicians", "tool.simulado-de-enfermagem4.desc": "Over 50 new questions from leading exam boards and institutions, with a timer and final percentage score.",
      "tool.simulado-de-enfermagem2.titulo": "1st Practice Exam for Nurses", "tool.simulado-de-enfermagem2.desc": "50 questions from leading exam boards and institutions, with a timer and final percentage score.",
      "tool.simulado-de-enfermagem3.titulo": "2nd (New) Practice Exam for Nurses", "tool.simulado-de-enfermagem3.desc": "Over 50 new questions from leading exam boards and institutions, with a timer and final percentage score.",
      "tool.simulado-de-enfermagem-nucleo-de-seguranca-do-paciente.titulo": "Patient Safety Practice Exam", "tool.simulado-de-enfermagem-nucleo-de-seguranca-do-paciente.desc": "50 questions from the Ministry of Health, IBSP, ANVISA and ISMP, with a timer and final percentage score.",
      "tool.simulado-de-enfermagem-doencas-de-notificacao-compulsoria.titulo": "Notifiable Diseases Practice Exam", "tool.simulado-de-enfermagem-doencas-de-notificacao-compulsoria.desc": "50 questions based on Ordinance GM/MS No. 6,734/2025.",
      "tool.simulado_vacinacao.titulo": "Vaccination Practice Exam", "tool.simulado_vacinacao.desc": "30 questions on vaccination (Ministry of Health & SBIM).",
      "tool.simulado_pcr.titulo": "Cardiac Arrest Practice Exam", "tool.simulado_pcr.desc": "30 questions on cardiopulmonary arrest (Exam boards/AHA & SBC).",
      "tool.simulado_bloco-operatorio.titulo": "Operating Room Practice Exam", "tool.simulado_bloco-operatorio.desc": "30 questions on the Operating Room (Exam boards/SOBECC/COFEN).",
      "tool.flashcards_quiz.titulo": "Interactive Nursing Question Quiz", "tool.flashcards_quiz.desc": "Interactive questions on various nursing topics.",
      "tool.biblioteca-provas.titulo": "Nursing Exam Library", "tool.biblioteca-provas.desc": "Access a vast collection of nursing exams and exercises.",
      "cat.esc.eyebrow": "Protocols", "cat.esc.titulo": "Assessment Scales — Patient Evaluation",
      "tool.aldrete.titulo": "Aldrete-Kroulik Score", "tool.aldrete.desc": "Patient assessment in the PACU.",
      "tool.apache.titulo": "APACHE II Score", "tool.apache.desc": "Severity assessment for critically ill patients.",
      "tool.apgar.titulo": "Apgar Score", "tool.apgar.desc": "Newborn assessment.",
      "tool.asa.titulo": "ASA Perioperative Risk", "tool.asa.desc": "Preoperative physical status classification.",
      "tool.ballard.titulo": "Ballard Score", "tool.ballard.desc": "Assessment of newborn neuromuscular and physical maturity.",
      "tool.barthel.titulo": "Barthel Index", "tool.barthel.desc": "Assesses the patient's degree of functional dependence.",
      "tool.bps.titulo": "Behavioural Pain Scale (BPS)", "tool.bps.desc": "Pain assessment in mechanically ventilated patients.",
      "tool.berg.titulo": "Berg Balance Scale (BBS)", "tool.berg.desc": "Assesses a patient's static and dynamic balance.",
      "tool.bishop.titulo": "Bishop Score", "tool.bishop.desc": "Assesses cervical maturity and readiness for labor.",
      "tool.braden.titulo": "Braden Scale", "tool.braden.desc": "Pressure injury risk.",
      "tool.cam.titulo": "CAM-ICU", "tool.cam.desc": "ICU delirium assessment.",
      "tool.capurro.titulo": "Capurro Method", "tool.capurro.desc": "Method for estimating newborn gestational age.",
      "tool.cincinnati.titulo": "Cincinnati Stroke Scale", "tool.cincinnati.desc": "Stroke assessment.",
      "tool.copsoq.titulo": "COPSOQ II", "tool.copsoq.desc": "Psychosocial risk management (NR-1).",
      "tool.copsoq3.titulo": "COPSOQ III", "tool.copsoq3.desc": "Psychosocial risk management (NR-1).",
      "tool.cornell.titulo": "Cornell Scale", "tool.cornell.desc": "Depression rating in patients with dementia.",
      "tool.cries.titulo": "CRIES Scale", "tool.cries.desc": "Newborn pain assessment.",
      "tool.curb-65.titulo": "CURB-65 Score", "tool.curb-65.desc": "Severity assessment in community-acquired pneumonia.",
      "tool.downton.titulo": "Downton Fall Risk Index", "tool.downton.desc": "Assesses fall risk in elderly patients.",
      "tool.elpo.titulo": "ELPO Scale", "tool.elpo.desc": "Pressure injury assessment in the operating room.",
      "tool.fast.titulo": "FAST Scale", "tool.fast.desc": "Stroke risk assessment.",
      "tool.flacc.titulo": "FLACC Scale", "tool.flacc.desc": "Pain assessment in non-verbal children.",
      "tool.four.titulo": "FOUR Score", "tool.four.desc": "Neurological assessment.",
      "tool.fugulin.titulo": "Fugulin Scale (SCP)", "tool.fugulin.desc": "Assessment of patient care complexity.",
      "tool.gds.titulo": "Geriatric Depression Scale (GDS)", "tool.gds.desc": "Depression in geriatric patients.",
      "tool.glasgow.titulo": "Glasgow Coma Scale", "tool.glasgow.desc": "Level of consciousness.",
      "tool.gosnell.titulo": "Gosnell Scale", "tool.gosnell.desc": "Pressure injury risk.",
      "tool.hamilton.titulo": "Hamilton Scale", "tool.hamilton.desc": "Assesses the severity of anxiety symptoms.",
      "tool.hendrich.titulo": "Hendrich II Fall Risk Model", "tool.hendrich.desc": "Assesses fall risk.",
      "tool.humpty.titulo": "Humpty Dumpty Scale", "tool.humpty.desc": "Fall risk in pediatric patients.",
      "tool.johns.titulo": "Johns Hopkins Fall Risk Scale", "tool.johns.desc": "Assesses fall risk.",
      "tool.jouvet.titulo": "Jouvet Scale", "tool.jouvet.desc": "Coma/consciousness scale.",
      "tool.katz.titulo": "Katz Index", "tool.katz.desc": "Assessment of independence in ADLs.",
      "tool.lachs.titulo": "Lachs Scale", "tool.lachs.desc": "Assessment of functional capacity in the elderly.",
      "tool.lanss.titulo": "LANSS Pain Scale", "tool.lanss.desc": "Neuropathic pain assessment.",
      "tool.lawton.titulo": "Lawton Scale", "tool.lawton.desc": "Measures the degree of independence in IADLs in the elderly.",
      "tool.manchester.titulo": "Manchester Triage Scale", "tool.manchester.desc": "Patient care priority in emergency care units.",
      "tool.meem.titulo": "MMSE (Mini-Mental State Examination)", "tool.meem.desc": "Cognitive screening for deficits.",
      "tool.meows.titulo": "MEOWS Score", "tool.meows.desc": "Modified early obstetric warning score / assesses clinical deterioration.",
      "tool.moca.titulo": "MoCA (Montreal Cognitive Assessment)", "tool.moca.desc": "Screening for mild cognitive impairment (MCI).",
      "tool.morse.titulo": "Morse Fall Scale", "tool.morse.desc": "Fall risk.",
      "tool.news.titulo": "NEWS Score", "tool.news.desc": "Adult early warning score / assesses clinical deterioration.",
      "tool.nihss.titulo": "NIHSS", "tool.nihss.desc": "Stroke assessment.",
      "tool.nips.titulo": "NIPS Scale", "tool.nips.desc": "Tool for assessing pain in newborns.",
      "tool.norton.titulo": "Norton Scale", "tool.norton.desc": "Pressure injury risk.",
      "tool.escalanumerica.titulo": "Numeric Pain Scale", "tool.escalanumerica.desc": "Numeric pain rating scale.",
      "tool.ofras.titulo": "OFRAS Scale", "tool.ofras.desc": "Fall risk in obstetric patients.",
      "tool.painad.titulo": "PAINAD Scale", "tool.painad.desc": "Pain assessment in advanced dementia.",
      "tool.pelod.titulo": "PELOD Score", "tool.pelod.desc": "Early severity and risk in children in the PICU.",
      "tool.pews.titulo": "PEWS Score", "tool.pews.desc": "Pediatric early warning score / assesses clinical deterioration.",
      "tool.perroca.titulo": "Perroca Patient Classification (SCP)", "tool.perroca.desc": "Patient classification according to care complexity.",
      "tool.prism.titulo": "PRISM Score", "tool.prism.desc": "Mortality risk in the PICU.",
      "tool.qsofa.titulo": "qSOFA Score", "tool.qsofa.desc": "Rapid sepsis screening.",
      "tool.ramsay.titulo": "Ramsay Scale", "tool.ramsay.desc": "Sedation assessment in patients.",
      "tool.rancholosamigos.titulo": "Rancho Los Amigos Scale", "tool.rancholosamigos.desc": "Cognitive and behavioral patterns in patients with brain injury.",
      "tool.richmond.titulo": "Richmond Agitation-Sedation Scale", "tool.richmond.desc": "Sedation and agitation.",
      "tool.saps.titulo": "SAPS III Score", "tool.saps.desc": "ICU mortality index percentage.",
      "tool.silverman.titulo": "Silverman-Anderson Score", "tool.silverman.desc": "Degree of respiratory distress in newborns.",
      "tool.sofa.titulo": "SOFA Score", "tool.sofa.desc": "Organ dysfunction in sepsis.",
      "tool.tinetti.titulo": "Tinetti Scale (POMA)", "tool.tinetti.desc": "Assesses fall risk in the elderly by observing gait and balance.",
      "tool.waterlow.titulo": "Waterlow Scale", "tool.waterlow.desc": "Pressure injury risk.",
      "tool.downes.titulo": "Wood-Downes Scale", "tool.downes.desc": "Respiratory distress in newborns.",
      "tool.zarit.titulo": "Zarit Burden Interview", "tool.zarit.desc": "Assessment of family caregiver burden.",
      "global.eyebrow": "Community", "global.titulo": "A global platform",
      "global.desc": "We connect professionals, institutions and knowledge across more than 195 countries, promoting stronger, more collaborative and sustainable nursing.",
      "global.link": "Our journey", "global.stat1": "Connected countries", "global.stat2": "Professionals impacted", "global.stat3": "Languages available",
      "newsletter2.titulo": "Get exclusive news and content", "newsletter2.desc": "Stay up to date with updates, news and new releases.",
      "newsletter2.consent": "I agree to receive email communications and accept the <a href=\"#\" style=\"color:#fff; text-decoration:underline;\">Privacy Policy</a>.",
      "hero.eyebrow": "Nursing Global Platform",
      "hero.title": 'Technology and knowledge for <span class="accent">more efficient, sustainable nursing.</span>',
      "hero.lead": "The Nursing Calculators Global Platform offers tools, content and digital solutions to transform professional practice and generate a positive impact on health.",
      "hero.btn1": "Explore tools", "hero.btn2": "About the platform",
      "hero.stat1": "Countries connected", "hero.stat2strong": "Millions", "hero.stat2": "Professionals impacted",
      "hero.stat3": "Digital tools", "hero.stat4strong": "Updated", "hero.stat4": "Evidence-based",
      "footer.institucional": "Institutional", "footer.recursos": "Resources", "footer.suporte": "Support", "footer.newsletter": "Newsletter",
      "footer.newsletter-desc": "Get exclusive content on nursing, management and health.",
      "footer.email-ph": "Your email", "footer.inscrever": "Subscribe",
      "footer.brand-desc": "Technology and knowledge for more efficient, sustainable nursing.",
      "footer.rights": "All rights reserved."
    },
    es: {
      "nav.inicio": "Inicio", "nav.assistencia": "Asistencia", "nav.educacao": "Educación",
      "nav.faleconosco": "Contacto", "nav.pesquisa": "Buscar", "nav.idiomas": "Idiomas", "nav.ferramentas": "Herramientas",
      "nav.gestao": "Gestión", "nav.recursos": "Recursos", "nav.institucional": "Institucional",
      "nav.entrar": "Iniciar sesión", "nav.criar": "Crear cuenta",
      "aria.busca": "Abrir búsqueda", "aria.idiomas": "Seleccionar idioma", "aria.idiomasDropdown": "Selector de idiomas",
      "aria.menu": "Abrir menú", "aria.navPrincipal": "Navegación principal", "aria.buscarInput": "Buscar en el sitio",
      "aria.mobileMenu": "Menú móvil",
      "busca.titulo": "Buscar en el sitio", "busca.placeholder": "Escribe lo que buscas...",
      "busca.btn": "Buscar", "busca.populares": "Búsquedas populares",
      "idiomas.regiao": "Región", "idiomas.paises": "Países de la región",
      "mega.subPrincipais": "Submenús principales", "mega.demaisNav": "Más navegación",
      "contact.sobre": "Sobre la plataforma", "contact.ajuda": "Centro de ayuda",
      "mobile.buscarPh": "Buscar...",
      "content.avaliar": "Evalúa este contenido", "content.leitura": "Leer", "content.compartilhar": "Compartir",
      "content.salvar": "Guardar", "content.imprimir": "Imprimir",
      "aria.fechar": "Cerrar", "aria.fonteDec": "Disminuir tamaño de fuente", "aria.fonteInc": "Aumentar tamaño de fuente",
      "aria.star5": "5 estrellas", "aria.star4": "4 estrellas", "aria.star3": "3 estrellas", "aria.star2": "2 estrellas", "aria.star1": "1 estrella",
      "a11y.tituloModal": "Preferencias de accesibilidad",
      "a11y.introModal": "Ajusta la visualización del sitio según tu preferencia. Tus elecciones se guardan en este navegador.",
      "a11y.fonteTitulo": "Tamaño de fuente", "a11y.fonteDesc": "Aumenta o disminuye el tamaño del texto en todo el sitio.",
      "a11y.contrasteTitulo": "Alto contraste", "a11y.contrasteDesc": "Aumenta el contraste de colores para mejorar la legibilidad.",
      "a11y.temaTitulo": "Modo oscuro", "a11y.temaDesc": "Cambia la visualización a un tema con fondo oscuro.",
      "a11y.dislexiaTitulo": "Fuente para dislexia", "a11y.dislexiaDesc": "Reemplaza la tipografía por una fuente de lectura facilitada.",
      "a11y.redefinir": "Restablecer todo", "a11y.atalhos": "Atajos de teclado",
      "a11y.atalhosTitulo": "Atajos de teclado",
      "a11y.atalho1": "Navegar entre elementos", "a11y.atalho2": "Cerrar menús, modales y el menú móvil",
      "a11y.atalho3": "Activar botones y enlaces", "a11y.atalho4": "Moverse entre los elementos del menú",
      "cookie.aviso": "Aviso de cookies",
      "cookie.bannerText": '<strong>Utilizamos cookies.</strong> Utilizamos cookies esenciales y, con tu consentimiento, cookies de rendimiento y personalización para mejorar tu experiencia. Más información en nuestra <a href="#">Política de Privacidad</a>.',
      "cookie.personalizar": "Personalizar", "cookie.rejeitar": "Rechazar no esenciales", "cookie.aceitar": "Aceptar todo",
      "cookie.modalTitulo": "Preferencias de cookies",
      "cookie.modalIntro": "Elige qué categorías de cookies permites. Las cookies esenciales no se pueden desactivar porque son necesarias para el funcionamiento de la plataforma.",
      "cookie.essenciaisTitulo": "Esenciales", "cookie.essenciaisDesc": "Necesarias para el inicio de sesión, la seguridad y el funcionamiento básico de la plataforma.",
      "cookie.desempenhoTitulo": "Rendimiento", "cookie.desempenhoDesc": "Ayudan a entender cómo los visitantes usan la plataforma para mejorarla continuamente.",
      "cookie.funcionalidadeTitulo": "Funcionalidad", "cookie.funcionalidadeDesc": "Recuerdan preferencias como idioma, región y tamaño de fuente.",
      "cookie.analiseTitulo": "Análisis y Publicidad", "cookie.analiseDesc": "Utilizados de forma agregada para entender las tendencias de uso de la plataforma.",
      "cookie.salvar": "Guardar preferencias",
      "herosearch.titulo": "¿Qué necesitas hoy?",
      "herosearch.placeholder": "Ej.: Goteo, Escala de Braden, Insulina, PAE...",
      "seo.h1": "Calculadoras de Enfermería, Simulacros y Escalas Clínicas",
      "seo.desc": "Plataforma completa con calculadoras de enfermería, escalas clínicas, cálculo de dosis de medicamentos y simulacros de exámenes públicos. Ideal para estudiantes, técnicos y enfermeros que buscan optimizar la práctica diaria, reforzar la seguridad del paciente y prepararse para exámenes.",
      "sol.eyebrow": "Sobre la plataforma",
      "sol.titulo": "Soluciones para cada momento de tu práctica",
      "sol.desc": "Herramientas clínicas, protocolos, escalas y contenido educativo para estudiantes, enfermeros, gestores e instituciones de salud — con responsabilidad digital e impacto medible.",
      "sol.card1.titulo": "Alcance Global", "sol.card1.desc": "Traducido a más de 18 idiomas, abarcando más de 140 países.",
      "sol.card2.titulo": "Escalas Clínicas", "sol.card2.desc": "Más de 60 escalas clínicas y asistenciales automatizadas.",
      "sol.card3.titulo": "Calculadoras", "sol.card3.desc": "Más de 15 calculadoras asistenciales para resolver cálculos de la rutina de la profesión.",
      "sol.card4.titulo": "Simulacros", "sol.card4.desc": "Simulacros interactivos de las principales entidades examinadoras, divididos por temas con evaluación de tiempo y aciertos.",
      "sol.card5.titulo": "Biblioteca", "sol.card5.desc": "Acervo en construcción para servir de base exclusiva de contenidos literarios en enfermería.",
      "sol.card6.titulo": "Enseñanza", "sol.card6.desc": "Compromiso con la enseñanza a través del desarrollo de contenidos literarios exclusivos.",
      "sol.card7.titulo": "Responsabilidad", "sol.card7.desc": "Créditos a la literatura y uso de referencias bibliográficas para orientar escalas y contenidos.",
      "sol.card8.titulo": "Seguridad y Privacidad", "sol.card8.desc": "Protección de la información y gobernanza de datos en todas las herramientas de la plataforma.",
      "quick.eyebrow": "Acceso rápido", "quick.titulo": "Herramientas más utilizadas", "quick.desc": "Accede a calculadoras y recursos validados que facilitan tu día a día.",
      "quick.link": "Ver todas las herramientas",
      "quick.card1": "Cálculo de Medicación", "quick.card2": "Goteo de Sueros", "quick.card3": "Índices y Escalas", "quick.card4": "Balance Hídrico",
      "quick.card5": "Exámenes de Laboratorio", "quick.card6": "Cálculo de Insulina", "quick.card7": "Cálculo de IMC", "quick.card8": "Todas las Herramientas",
      "edu.eyebrow": "Educación", "edu.titulo": "Educación que transforma", "edu.desc": "Contenidos actualizados, basados en evidencia y desarrollados por especialistas.",
      "edu.list1": "Biblioteca de exámenes de enfermería", "edu.list2": "Quiz interactivo de preguntas", "edu.list3": "Simulacros por entidad e institución", "edu.list4": "Diagnósticos de Enfermería — NANDA",
      "edu.btn": "Acceder a contenidos",
      "gestao.eyebrow": "Gestión", "gestao.titulo": "Gestión que genera impacto", "gestao.desc": "Recursos e indicadores para apoyar a líderes e instituciones de salud.",
      "gestao.list1": "Dimensionamiento del equipo de enfermería", "gestao.list2": "Escala de Fugulin — complejidad asistencial", "gestao.list3": "Clasificación de paciente — Perroca (SCP)", "gestao.list4": "SBAR — cambio de turno",
      "gestao.btn": "Conocer soluciones",
      "cat.calc.eyebrow": "Herramientas de apoyo", "cat.calc.titulo": "Calculadoras — Enfermería Práctica",
      "tool.balancohidrico.titulo": "Calcule el Balance Hídrico", "tool.balancohidrico.desc": "Control preciso de líquidos.",
      "tool.dimensionamento.titulo": "Dimensionamiento de Enfermería", "tool.dimensionamento.desc": "Organice su equipo de enfermería.",
      "tool.exames_laboratoriais.titulo": "Calculadora de Exámenes de Laboratorio", "tool.exames_laboratoriais.desc": "Calcule los resultados de exámenes de laboratorio.",
      "tool.gasometria.titulo": "Calculadora de Gasometría Arterial", "tool.gasometria.desc": "Interpretación de gasometría arterial.",
      "tool.gotejamento.titulo": "Calculadora de Goteo", "tool.gotejamento.desc": "Calcule la velocidad de infusión.",
      "tool.gestacional.titulo": "Edad Gestacional y FPP", "tool.gestacional.desc": "Calcule la edad gestacional y la fecha probable de parto.",
      "tool.imc.titulo": "Cálculo de IMC", "tool.imc.desc": "Índice de Masa Corporal.",
      "tool.insulina.titulo": "Cálculo de Insulina", "tool.insulina.desc": "Cálculo de dosis de insulina.",
      "tool.medicamentos.titulo": "Cálculo de Medicamentos", "tool.medicamentos.desc": "Dosis y diluciones de fármacos.",
      "tool.calculadoravacina.titulo": "Vacunas del Niño", "tool.calculadoravacina.desc": "Tabla de vacunas automatizada.",
      "tool.notificacao-compulsoria.titulo": "Enfermedades de Notificación Obligatoria", "tool.notificacao-compulsoria.desc": "Lista interactiva de las Enfermedades y Afecciones de Notificación Obligatoria del Ministerio de Salud.",
      "tool.diagnosticosnanda.titulo": "Diagnósticos de Enfermería - NANDA", "tool.diagnosticosnanda.desc": "Lista de diagnósticos de enfermería - NANDA (2018).",
      "tool.sbar.titulo": "SBAR - Formulario de Cambio de Turno", "tool.sbar.desc": "Formulario digital de SBAR para enfermeros, complete e imprima.",
      "tool.calculo-de-ferias.titulo": "Calculadora de Vacaciones (Enfermería)", "tool.calculo-de-ferias.desc": "¿Cuál es el valor a recibir en las vacaciones?",
      "tool.adicional-noturno.titulo": "Calculadora de Adicional Nocturno (Enfermería)", "tool.adicional-noturno.desc": "Calcule el valor de su adicional nocturno.",
      "tool.calculo-hora-extra.titulo": "Calculadora de Horas Extras a Recibir (Enfermería)", "tool.calculo-hora-extra.desc": "Calcule el valor de sus horas extras a recibir.",
      "tool.calculo-rescisao.titulo": "Calculadora del Valor de la Liquidación (Enfermería)", "tool.calculo-rescisao.desc": "Calcule el valor de su liquidación contractual.",
      "cat.sim.eyebrow": "Preparación", "cat.sim.titulo": "Simulacros de Enfermería — Entidades e Instituciones",
      "tool.simulado-de-enfermagem.titulo": "1er Simulacro para Técnicos de Enfermería", "tool.simulado-de-enfermagem.desc": "50 preguntas de las principales entidades e instituciones, con cronómetro y evaluación final del porcentaje de aciertos.",
      "tool.simulado-de-enfermagem4.titulo": "2º (Nuevo) Simulacro para Técnicos de Enfermería", "tool.simulado-de-enfermagem4.desc": "Más de 50 preguntas nuevas de las principales entidades e instituciones, con cronómetro y evaluación final del porcentaje de aciertos.",
      "tool.simulado-de-enfermagem2.titulo": "1er Simulacro para Enfermeros", "tool.simulado-de-enfermagem2.desc": "50 preguntas de las principales entidades e instituciones, con cronómetro y evaluación final del porcentaje de aciertos.",
      "tool.simulado-de-enfermagem3.titulo": "2º (Nuevo) Simulacro para Enfermeros", "tool.simulado-de-enfermagem3.desc": "Más de 50 preguntas nuevas de las principales entidades e instituciones, con cronómetro y evaluación final del porcentaje de aciertos.",
      "tool.simulado-de-enfermagem-nucleo-de-seguranca-do-paciente.titulo": "Simulacro sobre Seguridad del Paciente", "tool.simulado-de-enfermagem-nucleo-de-seguranca-do-paciente.desc": "50 preguntas del Ministerio de Salud, IBSP, ANVISA e ISMP, con cronómetro y evaluación final del porcentaje de aciertos.",
      "tool.simulado-de-enfermagem-doencas-de-notificacao-compulsoria.titulo": "Simulacro sobre Enfermedades de Notificación Obligatoria", "tool.simulado-de-enfermagem-doencas-de-notificacao-compulsoria.desc": "50 preguntas de la Ordenanza GM/MS Nº 6.734/2025.",
      "tool.simulado_vacinacao.titulo": "Simulacro sobre Vacunas", "tool.simulado_vacinacao.desc": "30 preguntas sobre vacunación (MS y SBIM).",
      "tool.simulado_pcr.titulo": "Simulacro sobre PCR", "tool.simulado_pcr.desc": "30 preguntas sobre Paro Cardiorrespiratorio (Entidades/AHA y SBC).",
      "tool.simulado_bloco-operatorio.titulo": "Simulacro sobre Quirófano", "tool.simulado_bloco-operatorio.desc": "30 preguntas sobre Quirófano (Entidades/SOBECC/COFEN).",
      "tool.flashcards_quiz.titulo": "Quiz Interactivo de Preguntas de Enfermería", "tool.flashcards_quiz.desc": "Preguntas interactivas sobre diversos temas de enfermería.",
      "tool.biblioteca-provas.titulo": "Biblioteca de Exámenes de Enfermería", "tool.biblioteca-provas.desc": "Acceso a una amplia colección de exámenes y ejercicios de enfermería.",
      "cat.esc.eyebrow": "Protocolos", "cat.esc.titulo": "Escalas de Evaluación — Evaluación de Pacientes",
      "tool.aldrete.titulo": "Escala de Aldrete y Kroulik", "tool.aldrete.desc": "Evaluación del paciente en la SRPA.",
      "tool.apache.titulo": "Escala APACHE II", "tool.apache.desc": "Evaluación de la gravedad del paciente crítico.",
      "tool.apgar.titulo": "Escala de Apgar", "tool.apgar.desc": "Evaluación de recién nacidos.",
      "tool.asa.titulo": "Riesgo Perioperatorio - ASA", "tool.asa.desc": "Clasificación del estado físico preoperatorio.",
      "tool.ballard.titulo": "Escala de Ballard", "tool.ballard.desc": "Evaluación de la madurez neuromuscular y física del recién nacido.",
      "tool.barthel.titulo": "Índice de Barthel", "tool.barthel.desc": "Evalúa el grado de dependencia funcional del paciente.",
      "tool.bps.titulo": "Escala de Dolor Conductual (BPS)", "tool.bps.desc": "Evaluación del dolor en pacientes bajo ventilación mecánica.",
      "tool.berg.titulo": "Escala de Berg (BBS)", "tool.berg.desc": "Evalúa el equilibrio estático y dinámico de un paciente.",
      "tool.bishop.titulo": "Índice de Bishop", "tool.bishop.desc": "Evalúa la madurez del cuello uterino y la preparación para el parto.",
      "tool.braden.titulo": "Escala de Braden", "tool.braden.desc": "Riesgo de lesión por presión.",
      "tool.cam.titulo": "Escala CAM-ICU", "tool.cam.desc": "Evaluación de delirio en UCI.",
      "tool.capurro.titulo": "Método de Capurro", "tool.capurro.desc": "Método para estimar la edad gestacional de los recién nacidos.",
      "tool.cincinnati.titulo": "Escala de Cincinnati", "tool.cincinnati.desc": "Evaluación de ACV.",
      "tool.copsoq.titulo": "COPSOQ II", "tool.copsoq.desc": "Gestión de riesgos psicosociales (NR-1).",
      "tool.copsoq3.titulo": "COPSOQ III", "tool.copsoq3.desc": "Gestión de riesgos psicosociales (NR-1).",
      "tool.cornell.titulo": "Escala de Cornell", "tool.cornell.desc": "Clasificación de depresión en pacientes con demencia.",
      "tool.cries.titulo": "Escala CRIES", "tool.cries.desc": "Evaluación del dolor en recién nacidos.",
      "tool.curb-65.titulo": "Escala CURB-65", "tool.curb-65.desc": "Evaluación de gravedad en neumonía adquirida en la comunidad.",
      "tool.downton.titulo": "Escala de Downton", "tool.downton.desc": "Evalúa el riesgo de caída en pacientes ancianos.",
      "tool.elpo.titulo": "Escala ELPO", "tool.elpo.desc": "Evaluación de lesión por presión en quirófano.",
      "tool.fast.titulo": "Escala FAST", "tool.fast.desc": "Evaluación de riesgo de ACV.",
      "tool.flacc.titulo": "Escala FLACC", "tool.flacc.desc": "Evaluación del dolor en niños no verbales.",
      "tool.four.titulo": "Escala FOUR", "tool.four.desc": "Evaluación neurológica.",
      "tool.fugulin.titulo": "Escala de Fugulin (SCP)", "tool.fugulin.desc": "Evaluación del grado de complejidad del paciente.",
      "tool.gds.titulo": "Escala GDS", "tool.gds.desc": "Depresión del paciente geriátrico.",
      "tool.glasgow.titulo": "Escala de Coma de Glasgow", "tool.glasgow.desc": "Nivel de conciencia.",
      "tool.gosnell.titulo": "Escala de Gosnell", "tool.gosnell.desc": "Riesgo de lesión por presión.",
      "tool.hamilton.titulo": "Escala de Hamilton", "tool.hamilton.desc": "Evalúa la gravedad de los síntomas de ansiedad.",
      "tool.hendrich.titulo": "Escala de Hendrich II", "tool.hendrich.desc": "Evalúa el riesgo de caídas.",
      "tool.humpty.titulo": "Escala de Humpty Dumpty", "tool.humpty.desc": "Riesgo de caídas en pacientes pediátricos.",
      "tool.johns.titulo": "Escala de Johns", "tool.johns.desc": "Evalúa el riesgo de caída.",
      "tool.jouvet.titulo": "Escala de Jouvet", "tool.jouvet.desc": "Escala de coma/conciencia.",
      "tool.katz.titulo": "Índice de Katz", "tool.katz.desc": "Evaluación de autonomía en las ABVD.",
      "tool.lachs.titulo": "Escala de Lachs", "tool.lachs.desc": "Evaluación de la capacidad funcional del anciano.",
      "tool.lanss.titulo": "Escala LANSS", "tool.lanss.desc": "Evaluación del dolor neuropático.",
      "tool.lawton.titulo": "Escala de Lawton", "tool.lawton.desc": "Mide el grado de independencia en las AIVD en ancianos.",
      "tool.manchester.titulo": "Escala de Manchester", "tool.manchester.desc": "Prioridad de atención del paciente en unidades de urgencias.",
      "tool.meem.titulo": "Escala MEEM", "tool.meem.desc": "Cribado cognitivo de déficits.",
      "tool.meows.titulo": "Escala MEOWS", "tool.meows.desc": "Puntuación de alerta obstétrica temprana / evalúa el deterioro clínico.",
      "tool.moca.titulo": "Escala MoCA", "tool.moca.desc": "Cribado de deterioro cognitivo leve (DCL).",
      "tool.morse.titulo": "Escala de Morse", "tool.morse.desc": "Riesgo de caída.",
      "tool.news.titulo": "Escala NEWS", "tool.news.desc": "Puntuación de alerta temprana en adultos / evalúa el deterioro clínico.",
      "tool.nihss.titulo": "Escala NIHSS", "tool.nihss.desc": "Evaluación de ACV.",
      "tool.nips.titulo": "Escala NIPS", "tool.nips.desc": "Herramienta para evaluar el dolor en recién nacidos.",
      "tool.norton.titulo": "Escala de Norton", "tool.norton.desc": "Riesgo de lesión por presión.",
      "tool.escalanumerica.titulo": "Escala Numérica del Dolor", "tool.escalanumerica.desc": "Escala numérica de dolor.",
      "tool.ofras.titulo": "Escala OFRAS", "tool.ofras.desc": "Riesgo de caídas en pacientes obstétricas.",
      "tool.painad.titulo": "Escala PAINAD", "tool.painad.desc": "Evaluación del dolor en demencia avanzada.",
      "tool.pelod.titulo": "Escala PELOD", "tool.pelod.desc": "Gravedad y riesgo precoz en niños en la UCIP.",
      "tool.pews.titulo": "Escala PEWS", "tool.pews.desc": "Alerta clínica temprana pediátrica / evalúa el deterioro clínico.",
      "tool.perroca.titulo": "Clasificación de Paciente Perroca (SCP)", "tool.perroca.desc": "Clasificación del paciente según su complejidad.",
      "tool.prism.titulo": "Escala PRISM", "tool.prism.desc": "Riesgo de mortalidad en la UCIP.",
      "tool.qsofa.titulo": "Escala qSOFA", "tool.qsofa.desc": "Cribado rápido de sepsis.",
      "tool.ramsay.titulo": "Escala de Ramsay", "tool.ramsay.desc": "Evaluación de la sedación en pacientes.",
      "tool.rancholosamigos.titulo": "Escala de Rancho Los Amigos", "tool.rancholosamigos.desc": "Patrones cognitivos y conductuales de pacientes con lesión cerebral.",
      "tool.richmond.titulo": "Escala de Richmond", "tool.richmond.desc": "Sedación y agitación.",
      "tool.saps.titulo": "Escala SAPS III", "tool.saps.desc": "Porcentaje del índice de mortalidad en UCI.",
      "tool.silverman.titulo": "Boletín de Silverman y Anderson", "tool.silverman.desc": "Grado de dificultad respiratoria en el recién nacido.",
      "tool.sofa.titulo": "Escala SOFA", "tool.sofa.desc": "Disfunción orgánica en sepsis.",
      "tool.tinetti.titulo": "Escala de Tinetti (POMA)", "tool.tinetti.desc": "Evalúa el riesgo de caída en ancianos observando la marcha y el equilibrio.",
      "tool.waterlow.titulo": "Escala de Waterlow", "tool.waterlow.desc": "Riesgo de lesión por presión.",
      "tool.downes.titulo": "Escala de Wood y Downes", "tool.downes.desc": "Dificultad respiratoria en el recién nacido.",
      "tool.zarit.titulo": "Escala de Zarit", "tool.zarit.desc": "Evaluación del grado de sobrecarga del cuidador familiar.",
      "global.eyebrow": "Comunidad", "global.titulo": "Una plataforma global",
      "global.desc": "Conectamos profesionales, instituciones y conocimiento en más de 195 países, promoviendo una enfermería más fuerte, colaborativa y sostenible.",
      "global.link": "Nuestro recorrido", "global.stat1": "Países conectados", "global.stat2": "Profesionales impactados", "global.stat3": "Idiomas disponibles",
      "newsletter2.titulo": "Reciba novedades y contenidos exclusivos", "newsletter2.desc": "Manténgase al tanto de las actualizaciones, novedades y lanzamientos.",
      "newsletter2.consent": "Acepto recibir comunicaciones por correo electrónico y acepto la <a href=\"#\" style=\"color:#fff; text-decoration:underline;\">Política de Privacidad</a>.",
      "hero.eyebrow": "Nursing Global Platform",
      "hero.title": 'Tecnología y conocimiento para una enfermería <span class="accent">más eficiente y sostenible.</span>',
      "hero.lead": "La Plataforma Global de Calculadoras de Enfermería ofrece herramientas, contenidos y soluciones digitales para transformar la práctica profesional y generar un impacto positivo en la salud.",
      "hero.btn1": "Explorar herramientas", "hero.btn2": "Conocer la plataforma",
      "hero.stat1": "Países conectados", "hero.stat2strong": "Millones", "hero.stat2": "Profesionales impactados",
      "hero.stat3": "Herramientas digitales", "hero.stat4strong": "Actualizado", "hero.stat4": "Basado en evidencia",
      "footer.institucional": "Institucional", "footer.recursos": "Recursos", "footer.suporte": "Soporte", "footer.newsletter": "Boletín",
      "footer.newsletter-desc": "Recibe contenido exclusivo sobre enfermería, gestión y salud.",
      "footer.email-ph": "Tu correo", "footer.inscrever": "Suscribirse",
      "footer.brand-desc": "Tecnología y conocimiento para una enfermería más eficiente y sostenible.",
      "footer.rights": "Todos los derechos reservados."
    }
  };

  var ALL_LANG_CODES = ["pt-BR","en","es","fr","de","it","nl","pl","ru","tr","ar","he","hi","bn","zh-CN","zh-TW","ja","ko","vi","th","id","ms","tl","sw","am","el","ro","hu","cs","sv"];
  var SUPPORTED = ALL_LANG_CODES;

  // Regiões para o mega-menu de Idiomas (coluna 1 = região, coluna 2 = países da região)
  var REGIONS = [
    { id: "americas", name: "Américas", codes: ["pt-BR", "en", "es", "fr", "nl"] },
    { id: "europa", name: "Europa", codes: ["fr", "de", "it", "nl", "pl", "ru", "el", "ro", "hu", "cs", "sv", "en", "es", "pt-BR"] },
    { id: "asia", name: "Ásia-Pacífico", codes: ["hi", "bn", "zh-CN", "zh-TW", "ja", "ko", "vi", "th", "id", "ms", "tl", "en", "ar", "pt-BR"] },
    { id: "mea", name: "Oriente Médio & África", codes: ["tr", "ar", "he", "sw", "am", "en", "fr", "es", "pt-BR"] }
  ];

  // Países por região (coluna 2 do mega-menu Idiomas) — bandeira e nome do país
  // específicos, mesmo quando reaproveitam o idioma/dicionário de outro código.
  // Estrutura pronta para expansão gradual rumo aos 195 países (fase de i18n).
  var COUNTRIES = {
    americas: [
      { country: "Brasil", code: "pt-BR", flag: "br.webp" },
      { country: "Estados Unidos", code: "en", flag: "us.webp" },
      { country: "Canadá", code: "en", flag: "ca.webp" },
      { country: "México", code: "es", flag: "mx.webp" },
      { country: "Argentina", code: "es", flag: "ar.webp" },
      { country: "Colômbia", code: "es", flag: "co.webp" },
      { country: "Chile", code: "es", flag: "cl.webp" },
      { country: "Peru", code: "es", flag: "pe.webp" },
      { country: "Equador", code: "es", flag: "ec.webp" },
      { country: "Venezuela", code: "es", flag: "ve.webp" },
      { country: "Uruguai", code: "es", flag: "uy.webp" },
      { country: "Paraguai", code: "es", flag: "py.webp" },
      { country: "Bolívia", code: "es", flag: "bo.webp" },
      { country: "Costa Rica", code: "es", flag: "cr.webp" },
      { country: "Panamá", code: "es", flag: "pa.webp" },
      { country: "Guatemala", code: "es", flag: "gt.webp" },
      { country: "Cuba", code: "es", flag: "cu.webp" },
      { country: "Rep. Dominicana", code: "es", flag: "do.webp" },
      { country: "Honduras", code: "es", flag: "hn.webp" },
      { country: "Nicarágua", code: "es", flag: "ni.webp" },
      { country: "El Salvador", code: "es", flag: "sv.webp" },
      { country: "Haiti", code: "fr", flag: "ht.webp" },
      { country: "Jamaica", code: "en", flag: "jm.webp" },
      { country: "Trinidad e Tobago", code: "en", flag: "tt.webp" },
      { country: "Bahamas", code: "en", flag: "bs.webp" },
      { country: "Barbados", code: "en", flag: "bb.webp" },
      { country: "Granada", code: "en", flag: "gd.webp" },
      { country: "Suriname", code: "nl", flag: "sr.webp" },
      { country: "Guiana", code: "en", flag: "gy.webp" },
      { country: "Belize", code: "en", flag: "bz.webp" },
      { country: "Santa Lúcia", code: "en", flag: "lc.webp" },
      { country: "Dominica", code: "en", flag: "dm.webp" },
      { country: "Antígua e Barbuda", code: "en", flag: "ag.webp" },
      { country: "São Cristóvão e Névis", code: "en", flag: "kn.webp" },
      { country: "São Vicente e Granadinas", code: "en", flag: "vc.webp" },
    ],
    europa: [
      { country: "Portugal", code: "pt-BR", flag: "pt.webp" },
      { country: "Espanha", code: "es", flag: "es.webp" },
      { country: "França", code: "fr", flag: "fr.webp" },
      { country: "Bélgica", code: "fr", flag: "be.webp" },
      { country: "Alemanha", code: "de", flag: "de.webp" },
      { country: "Áustria", code: "de", flag: "at.webp" },
      { country: "Suíça", code: "de", flag: "ch.webp" },
      { country: "Itália", code: "it", flag: "it.webp" },
      { country: "Países Baixos", code: "nl", flag: "nl.webp" },
      { country: "Polônia", code: "pl", flag: "pl.webp" },
      { country: "Rússia", code: "ru", flag: "ru.webp" },
      { country: "Grécia", code: "el", flag: "gr.webp" },
      { country: "Romênia", code: "ro", flag: "ro.webp" },
      { country: "Hungria", code: "hu", flag: "hu.webp" },
      { country: "Rep. Tcheca", code: "cs", flag: "cz.webp" },
      { country: "Suécia", code: "sv", flag: "se.webp" },
      { country: "Noruega", code: "sv", flag: "no.webp" },
      { country: "Dinamarca", code: "sv", flag: "dk.webp" },
      { country: "Finlândia", code: "sv", flag: "fi.webp" },
      { country: "Irlanda", code: "en", flag: "ie.webp" },
      { country: "Reino Unido", code: "en", flag: "uk.webp" },
      { country: "Ucrânia", code: "ru", flag: "ua.webp" },
      { country: "Bulgária", code: "ru", flag: "bg.webp" },
      { country: "Croácia", code: "en", flag: "hr.webp" },
      { country: "Sérvia", code: "en", flag: "rs.webp" },
      { country: "Eslováquia", code: "cs", flag: "sk.webp" },
      { country: "Eslovênia", code: "en", flag: "si.webp" },
      { country: "Lituânia", code: "en", flag: "lt.webp" },
      { country: "Letônia", code: "en", flag: "lv.webp" },
      { country: "Estônia", code: "en", flag: "ee.webp" },
      { country: "Luxemburgo", code: "fr", flag: "lu.webp" },
      { country: "Malta", code: "en", flag: "mt.webp" },
      { country: "Chipre", code: "el", flag: "cy.webp" },
      { country: "Islândia", code: "en", flag: "is.webp" },
      { country: "Albânia", code: "en", flag: "al.webp" },
      { country: "Bósnia e Herzegovina", code: "en", flag: "ba.webp" },
      { country: "Moldávia", code: "ro", flag: "md.webp" },
      { country: "Macedônia do Norte", code: "en", flag: "mk.webp" },
      { country: "Montenegro", code: "en", flag: "me.webp" },
      { country: "Andorra", code: "es", flag: "ad.webp" },
      { country: "Mônaco", code: "fr", flag: "mc.webp" },
      { country: "Liechtenstein", code: "de", flag: "li.webp" },
      { country: "San Marino", code: "it", flag: "sm.webp" },
      { country: "Vaticano", code: "it", flag: "va.webp" },
      { country: "Belarus", code: "ru", flag: "by.webp" },
      { country: "Geórgia", code: "en", flag: "ge.webp" },
      { country: "Armênia", code: "ru", flag: "am.webp" },
      { country: "Azerbaijão", code: "ru", flag: "az.webp" },
      { country: "Kosovo", code: "en", flag: "xk.webp" },
    ],
    asia: [
      { country: "Índia", code: "hi", flag: "in.webp" },
      { country: "Bangladesh", code: "bn", flag: "bd.webp" },
      { country: "China", code: "zh-CN", flag: "cn.webp" },
      { country: "Taiwan", code: "zh-TW", flag: "tw.webp" },
      { country: "Japão", code: "ja", flag: "jp.webp" },
      { country: "Coreia do Sul", code: "ko", flag: "kr.webp" },
      { country: "Coreia do Norte", code: "ko", flag: "kp.webp" },
      { country: "Vietnã", code: "vi", flag: "vn.webp" },
      { country: "Tailândia", code: "th", flag: "th.webp" },
      { country: "Indonésia", code: "id", flag: "id.webp" },
      { country: "Malásia", code: "ms", flag: "my.webp" },
      { country: "Filipinas", code: "tl", flag: "ph.webp" },
      { country: "Cingapura", code: "en", flag: "sg.webp" },
      { country: "Austrália", code: "en", flag: "au.webp" },
      { country: "Nova Zelândia", code: "en", flag: "nz.webp" },
      { country: "Paquistão", code: "en", flag: "pk.webp" },
      { country: "Sri Lanka", code: "en", flag: "lk.webp" },
      { country: "Camboja", code: "en", flag: "kh.webp" },
      { country: "Mianmar", code: "en", flag: "mm.webp" },
      { country: "Laos", code: "en", flag: "la.webp" },
      { country: "Mongólia", code: "en", flag: "mn.webp" },
      { country: "Nepal", code: "hi", flag: "np.webp" },
      { country: "Butão", code: "en", flag: "bt.webp" },
      { country: "Maldivas", code: "en", flag: "mv.webp" },
      { country: "Afeganistão", code: "en", flag: "af.webp" },
      { country: "Irã", code: "ar", flag: "ir.webp" },
      { country: "Iraque", code: "ar", flag: "iq.webp" },
      { country: "Síria", code: "ar", flag: "sy.webp" },
      { country: "Líbano", code: "ar", flag: "lb.webp" },
      { country: "Jordânia", code: "ar", flag: "jo.webp" },
      { country: "Iêmen", code: "ar", flag: "ye.webp" },
      { country: "Omã", code: "ar", flag: "om.webp" },
      { country: "Kuwait", code: "ar", flag: "kw.webp" },
      { country: "Catar", code: "ar", flag: "qa.webp" },
      { country: "Bahrein", code: "ar", flag: "bh.webp" },
      { country: "Brunei", code: "ms", flag: "bn.webp" },
      { country: "Timor-Leste", code: "pt-BR", flag: "tl.webp" },
      { country: "Fiji", code: "en", flag: "fj.webp" },
      { country: "Papua Nova Guiné", code: "en", flag: "pg.webp" },
      { country: "Ilhas Salomão", code: "en", flag: "sb.webp" },
      { country: "Vanuatu", code: "en", flag: "vu.webp" },
      { country: "Samoa", code: "en", flag: "ws.webp" },
      { country: "Tonga", code: "en", flag: "to.webp" },
      { country: "Kiribati", code: "en", flag: "ki.webp" },
      { country: "Micronésia", code: "en", flag: "fm.webp" },
      { country: "Palau", code: "en", flag: "pw.webp" },
      { country: "Ilhas Marshall", code: "en", flag: "mh.webp" },
      { country: "Nauru", code: "en", flag: "nr.webp" },
      { country: "Tuvalu", code: "en", flag: "tv.webp" },
      { country: "Cazaquistão", code: "ru", flag: "kz.webp" },
      { country: "Uzbequistão", code: "ru", flag: "uz.webp" },
      { country: "Turcomenistão", code: "ru", flag: "tm.webp" },
      { country: "Quirguistão", code: "ru", flag: "kg.webp" },
      { country: "Tajiquistão", code: "ru", flag: "tj.webp" },
    ],
    mea: [
      { country: "Turquia", code: "tr", flag: "tr.webp" },
      { country: "Arábia Saudita", code: "ar", flag: "sa.webp" },
      { country: "Emirados Árabes", code: "ar", flag: "ae.webp" },
      { country: "Egito", code: "ar", flag: "eg.webp" },
      { country: "Israel", code: "he", flag: "il.webp" },
      { country: "Quênia", code: "sw", flag: "ke.webp" },
      { country: "Nigéria", code: "en", flag: "ng.webp" },
      { country: "África do Sul", code: "en", flag: "za.webp" },
      { country: "Etiópia", code: "am", flag: "et.webp" },
      { country: "Marrocos", code: "ar", flag: "ma.webp" },
      { country: "Gana", code: "en", flag: "gh.webp" },
      { country: "Argélia", code: "ar", flag: "dz.webp" },
      { country: "Tunísia", code: "ar", flag: "tn.webp" },
      { country: "Líbia", code: "ar", flag: "ly.webp" },
      { country: "Sudão", code: "ar", flag: "sd.webp" },
      { country: "Sudão do Sul", code: "en", flag: "ss.webp" },
      { country: "Somália", code: "sw", flag: "so.webp" },
      { country: "Tanzânia", code: "sw", flag: "tz.webp" },
      { country: "Uganda", code: "sw", flag: "ug.webp" },
      { country: "Ruanda", code: "sw", flag: "rw.webp" },
      { country: "Burundi", code: "sw", flag: "bi.webp" },
      { country: "Camarões", code: "fr", flag: "cm.webp" },
      { country: "Costa do Marfim", code: "fr", flag: "ci.webp" },
      { country: "Senegal", code: "fr", flag: "sn.webp" },
      { country: "Mali", code: "fr", flag: "ml.webp" },
      { country: "Burkina Faso", code: "fr", flag: "bf.webp" },
      { country: "Níger", code: "fr", flag: "ne.webp" },
      { country: "Chade", code: "ar", flag: "td.webp" },
      { country: "Rep. Centro-Africana", code: "fr", flag: "cf.webp" },
      { country: "Congo", code: "fr", flag: "cg.webp" },
      { country: "RD Congo", code: "fr", flag: "cd.webp" },
      { country: "Gabão", code: "fr", flag: "ga.webp" },
      { country: "Guiné Equatorial", code: "es", flag: "gq.webp" },
      { country: "São Tomé e Príncipe", code: "pt-BR", flag: "st.webp" },
      { country: "Lesoto", code: "en", flag: "ls.webp" },
      { country: "Eswatini", code: "en", flag: "sz.webp" },
      { country: "Botswana", code: "en", flag: "bw.webp" },
      { country: "Namíbia", code: "en", flag: "na.webp" },
      { country: "Zimbábue", code: "en", flag: "zw.webp" },
      { country: "Zâmbia", code: "en", flag: "zm.webp" },
      { country: "Malawi", code: "en", flag: "mw.webp" },
      { country: "Moçambique", code: "pt-BR", flag: "mz.webp" },
      { country: "Angola", code: "pt-BR", flag: "ao.webp" },
      { country: "Cabo Verde", code: "pt-BR", flag: "cv.webp" },
      { country: "Guiné-Bissau", code: "pt-BR", flag: "gw.webp" },
      { country: "Guiné", code: "fr", flag: "gn.webp" },
      { country: "Benim", code: "fr", flag: "bj.webp" },
      { country: "Togo", code: "fr", flag: "tg.webp" },
      { country: "Libéria", code: "en", flag: "lr.webp" },
      { country: "Serra Leoa", code: "en", flag: "sl.webp" },
      { country: "Gâmbia", code: "en", flag: "gm.webp" },
      { country: "Mauritânia", code: "ar", flag: "mr.webp" },
      { country: "Djibuti", code: "ar", flag: "dj.webp" },
      { country: "Eritreia", code: "ar", flag: "er.webp" },
      { country: "Comores", code: "ar", flag: "km.webp" },
      { country: "Madagascar", code: "en", flag: "mg.webp" },
      { country: "Maurício", code: "en", flag: "mu.webp" },
      { country: "Seychelles", code: "en", flag: "sc.webp" },
      { country: "Bahamas", code: "en", flag: "bs.webp" },
    ],
  };

  // Nomes de regiões e países traduzidos (o widget é gerado via JS, então os
  // nomes não passam pelo mecanismo padrão de [data-i18n] — precisam deste
  // dicionário próprio, aplicado em refreshLangPanelLabels()).
  var REGION_NAMES = {
    en: { americas: "Americas", europa: "Europe", asia: "Asia-Pacific", mea: "Middle East & Africa" },
    es: { americas: "Américas", europa: "Europa", asia: "Asia-Pacífico", mea: "Oriente Medio y África" },
    fr: { americas: "Amériques", europa: "Europe", asia: "Asie-Pacifique", mea: "Moyen-Orient et Afrique" },
    de: { americas: "Amerikas", europa: "Europa", asia: "Asien-Pazifik", mea: "Naher Osten & Afrika" },
    it: { americas: "Americhe", europa: "Europa", asia: "Asia-Pacifico", mea: "Medio Oriente e Africa" },
    nl: { americas: "Amerika's", europa: "Europa", asia: "Azië-Pacifisch", mea: "Midden-Oosten & Afrika" },
    pl: { americas: "Ameryki", europa: "Europa", asia: "Azja-Pacyfik", mea: "Bliski Wschód i Afryka" },
    ru: { americas: "Америки", europa: "Европа", asia: "Азия-Тихоокеанский", mea: "Ближний Восток и Африка" },
    tr: { americas: "Amerikalar", europa: "Avrupa", asia: "Asya-Pasifik", mea: "Orta Doğu ve Afrika" },
    ar: { americas: "الأمريكتان", europa: "أوروبا", asia: "آسيا والمحيط الهادئ", mea: "الشرق الأوسط وأفريقيا" },
    he: { americas: "אמריקות", europa: "אירופה", asia: "אסיה-פסיפיק", mea: "המזרח התיכון ואפריקה" },
    hi: { americas: "अमेरिकास", europa: "यूरोप", asia: "एशिया-प्रशांत", mea: "मध्य पूर्व और अफ्रीका" },
    bn: { americas: "আমেরিকা", europa: "ইউরোপ", asia: "এশিয়া-প্রশান্ত", mea: "মধ্যপ্রাচ্য ও আফ্রিকা" },
    zh-CN: { americas: "美洲", europa: "欧洲", asia: "亚太", mea: "中东和非洲" },
    zh-TW: { americas: "美洲", europa: "歐洲", asia: "亞太", mea: "中東和非洲" },
    ja: { americas: "アメリカ大陸", europa: "ヨーロッパ", asia: "アジア太平洋", mea: "中東およびアフリカ" },
    ko: { americas: "아메리카", europa: "유럽", asia: "아시아-태평양", mea: "중동 및 아프리카" },
    vi: { americas: "Châu Mỹ", europa: "Châu Âu", asia: "Châu Á-Thái Bình Dương", mea: "Trung Đông và Châu Phi" },
    th: { americas: "อเมริกา", europa: "ยุโรป", asia: "เอเชีย-แปซิฟิก", mea: "ตะวันออกกลางและแอฟริกา" },
    id: { americas: "Amerika", europa: "Eropa", asia: "Asia-Pasifik", mea: "Timur Tengah & Afrika" },
    ms: { americas: "Amerika", europa: "Eropah", asia: "Asia-Pasifik", mea: "Timur Tengah & Afrika" },
    tl: { americas: "Americas", europa: "Europa", asia: "Asya-Pasipiko", mea: "Gitnang Silangan at Africa" },
    sw: { americas: "Marekani", europa: "Ulaya", asia: "Asia-Pasifiki", mea: "Mashariki ya Kati & Afrika" },
    am: { americas: "አሜሪካ", europa: "አውሮፓ", asia: "እስያ-ፓሲፊክ", mea: "መካከለኛው ምስራቅ እና አፍሪካ" },
    el: { americas: "Αμερικές", europa: "Ευρώπη", asia: "Ασία-Ειρηνικός", mea: "Μέση Ανατολή και Αφρική" },
    ro: { americas: "Americile", europa: "Europa", asia: "Asia-Pacifica", mea: "Orientul Mijlociu și Africa" },
    hu: { americas: "Amerikák", europa: "Európa", asia: "Ázsia-Csendes-óceáni", mea: "Közel-Kelet és Afrika" },
    cs: { americas: "Ameriky", europa: "Evropa", asia: "Asie-Pacifik", mea: "Blízký východ a Afrika" },
    sv: { americas: "Amerika", europa: "Europa", asia: "Asien-Stillahavet", mea: "Mellanöstern och Afrika" },
  };;

  var COUNTRY_NAMES = {
    en: {
      br: "Brazil", us: "United States", ca: "Canada", mx: "Mexico", ar: "Argentina", co: "Colombia",
      cl: "Chile", pe: "Peru", ec: "Ecuador", ve: "Venezuela", uy: "Uruguay", py: "Paraguay",
      bo: "Bolivia", cr: "Costa Rica", pa: "Panama", gt: "Guatemala", cu: "Cuba", do: "Dominican Republic",
      pt: "Portugal", es: "Spain", fr: "France", be: "Belgium", de: "Germany", at: "Austria",
      ch: "Switzerland", it: "Italy", nl: "Netherlands", pl: "Poland", ru: "Russia", gr: "Greece",
      ro: "Romania", hu: "Hungary", cz: "Czech Republic", se: "Sweden", no: "Norway", dk: "Denmark",
      fi: "Finland", ie: "Ireland", uk: "United Kingdom", ua: "Ukraine", bg: "Bulgaria", hr: "Croatia",
      in: "India", bd: "Bangladesh", cn: "China", tw: "Taiwan", jp: "Japan", kr: "South Korea",
      vn: "Vietnam", th: "Thailand", id: "Indonesia", my: "Malaysia", ph: "Philippines", sg: "Singapore",
      au: "Australia", nz: "New Zealand", pk: "Pakistan", lk: "Sri Lanka", kh: "Cambodia", mm: "Myanmar",
      tr: "Turkey", sa: "Saudi Arabia", ae: "United Arab Emirates", eg: "Egypt", il: "Israel", ir: "Iran",
      ke: "Kenya", ng: "Nigeria", za: "South Africa", et: "Ethiopia", ma: "Morocco", gh: "Ghana"
    },
    es: {
      br: "Brasil", us: "Estados Unidos", ca: "Canadá", mx: "México", ar: "Argentina", co: "Colombia",
      cl: "Chile", pe: "Perú", ec: "Ecuador", ve: "Venezuela", uy: "Uruguay", py: "Paraguay",
      bo: "Bolivia", cr: "Costa Rica", pa: "Panamá", gt: "Guatemala", cu: "Cuba", do: "República Dominicana",
      pt: "Portugal", es: "España", fr: "Francia", be: "Bélgica", de: "Alemania", at: "Austria",
      ch: "Suiza", it: "Italia", nl: "Países Bajos", pl: "Polonia", ru: "Rusia", gr: "Grecia",
      ro: "Rumanía", hu: "Hungría", cz: "República Checa", se: "Suecia", no: "Noruega", dk: "Dinamarca",
      fi: "Finlandia", ie: "Irlanda", uk: "Reino Unido", ua: "Ucrania", bg: "Bulgaria", hr: "Croacia",
      in: "India", bd: "Bangladés", cn: "China", tw: "Taiwán", jp: "Japón", kr: "Corea del Sur",
      vn: "Vietnam", th: "Tailandia", id: "Indonesia", my: "Malasia", ph: "Filipinas", sg: "Singapur",
      au: "Australia", nz: "Nueva Zelanda", pk: "Pakistán", lk: "Sri Lanka", kh: "Camboya", mm: "Myanmar",
      tr: "Turquía", sa: "Arabia Saudita", ae: "Emiratos Árabes Unidos", eg: "Egipto", il: "Israel", ir: "Irán",
      ke: "Kenia", ng: "Nigeria", za: "Sudáfrica", et: "Etiopía", ma: "Marruecos", gh: "Ghana"
    }
  };

  var LANG_NOTE = {
    "pt-BR": "Tradução ativa para 28 idiomas e 195 países. Selecione seu país para localizar a interface.",
    "en": "Active translation for 28 languages and 195 countries. Select your country to localize the interface.",
    "es": "Traducción activa para 28 idiomas y 195 países. Seleccione su país para localizar la interfaz.",
    "fr": "Traduction active pour 28 langues et 195 pays. Sélectionnez votre pays pour localiser l'interface.",
    "de": "Aktive Übersetzung für 28 Sprachen und 195 Länder. Wählen Sie Ihr Land, um die Oberfläche zu lokalisieren.",
    "it": "Traduzione attiva per 28 lingue e 195 paesi. Seleziona il tuo paese per localizzare l'interfaccia.",
    "nl": "Actieve vertaling voor 28 talen en 195 landen. Selecteer uw land om de interface te lokaliseren.",
    "pl": "Aktywne tłumaczenie na 28 języków i 195 krajów. Wybierz swój kraj, aby zlokalizować interfejs.",
    "ru": "Активный перевод на 28 языков и 195 стран. Выберите свою страну для локализации интерфейса.",
    "tr": "28 dil ve 195 ülke için aktif çeviri. Arayüzü yerelleştirmek için ülkenizi seçin.",
    "ar": "ترجمة نشطة لـ 28 لغة و 195 دولة. اختر بلدك لتوطين الواجهة.",
    "he": "תרגום פעיל ל-28 שפות ו-195 מדינות. בחר את מדינתך כדי להתאים את הממשק.",
    "hi": "28 भाषाओं और 195 देशों के लिए सक्रिय अनुवाद। इंटरफ़ेस को स्थानीयकृत करने के लिए अपना देश चुनें।",
    "bn": "28 ভাষা এবং 195 দেশের জন্য সক্রিয় অনুবাদ। ইন্টারফেস স্থানীয়করণ করতে আপনার দেশ নির্বাচন করুন।",
    "zh-CN": "28种语言和195个国家的活跃翻译。选择您的国家以本地化界面。",
    "zh-TW": "28種語言和195個國家的活躍翻譯。選擇您的國家以本地化界面。",
    "ja": "28言語・195カ国の翻訳が利用可能です。インターフェイスをローカライズするには国を選択してください。",
    "ko": "28개 언어 및 195개국에 대한 활성 번역. 인터페이스를 현지화하려면 국가를 선택하세요.",
    "vi": "Dịch thuật hoạt động cho 28 ngôn ngữ và 195 quốc gia. Chọn quốc gia của bạn để địa phương hóa giao diện.",
    "th": "แปลภาษาสำหรับ 28 ภาษาและ 195 ประเทศ เลือกประเทศของคุณเพื่อปรับอินเทอร์เฟซ",
    "id": "Terjemahan aktif untuk 28 bahasa dan 195 negara. Pilih negara Anda untuk melokalkan antarmuka.",
    "ms": "Terjemahan aktif untuk 28 bahasa dan 195 negara. Pilih negara anda untuk menyetempatkan antara muka.",
    "tl": "Aktibong pagsasalin para sa 28 wika at 195 bansa. Piliin ang iyong bansa upang i-localize ang interface.",
    "sw": "Tafsiri hai kwa lugha 28 na nchi 195. Chagua nchi yako kuifanya kiolesha kiwe cha eneo lako.",
    "am": "ለ28 ቋንቋዎች እና ለ195 ሀገራት ንቁ ትርጉም። በይነገጹን ለአካባቢዎ ለማስማማ ሀገርዎን ይምረጡ።",
    "el": "Ενεργή μετάφραση για 28 γλώσσες και 195 χώρες. Επιλέξτε τη χώρα σας για μετάφραση της διεπαφής.",
    "ro": "Traducere activă pentru 28 limbi și 195 țări. Selectați țara dvs. pentru a localiza interfața.",
    "hu": "Aktív fordítás 28 nyelvre és 195 országra. Válassza országát az felület lokalizálásához.",
    "cs": "Aktivní překlad pro 28 jazyků a 195 zemí. Vyberte svou zemi pro lokalizaci rozhraní.",
    "sv": "Aktiv översättning för 28 språk och 195 länder. Välj ditt land för att lokalisera gränssnittet.",
  };;

  // Reaplica os nomes de região/país e a nota do painel de Idiomas no idioma
  // atual (o conteúdo é gerado via JS, fora do mecanismo padrão [data-i18n]).
  function refreshLangPanelLabels() {
    var lang = currentLang();
    var regionListEl = document.getElementById("gh-region-list");
    var gridEl = document.getElementById("gh-lang-grid");

    if (regionListEl) {
      regionListEl.querySelectorAll("button[data-region]").forEach(function (btn) {
        var rid = btn.getAttribute("data-region");
        var region = REGIONS.filter(function (r) { return r.id === rid; })[0];
        var fallback = region ? region.name : btn.textContent;
        btn.textContent = (REGION_NAMES[lang] && REGION_NAMES[lang][rid]) || fallback;
      });
    }
    if (gridEl) {
      gridEl.querySelectorAll("button[data-flag]").forEach(function (btn) {
        var id = (btn.getAttribute("data-flag") || "").replace(".webp", "");
        var span = btn.querySelector("span");
        if (!span) return;
        var fallback = btn.getAttribute("data-country") || span.textContent;
        span.textContent = (COUNTRY_NAMES[lang] && COUNTRY_NAMES[lang][id]) || fallback;
      });
    }
    var note = document.getElementById("gh-lang-note");
    if (note) note.textContent = LANG_NOTE[lang] || LANG_NOTE["pt-BR"];
  }

  function currentLang() {
    return localStorage.getItem("site-lang") || "pt-BR";
  }

  function applyLanguage(code, displayName, flagFile) {
    // For embedded languages (en, es) use TRANSLATIONS directly.
    // For all others, async-load the JSON dictionary then apply.
    if (TRANSLATIONS[code] || code === "pt-BR") {
      _doApplyLanguage(code, displayName, flagFile);
    } else {
      // Try i18n-loader, fall back to en
      var loader = window.I18N_LOADER;
      if (loader) {
        loader.fetchDict(code).then(function(dict) {
          if (dict) {
            TRANSLATIONS[code] = dict;
            _doApplyLanguage(code, displayName, flagFile);
          } else if (code !== "en") {
            _doApplyLanguage("en", displayName, flagFile);
          }
        });
      } else {
        // No loader — fetch directly
        fetch("i18n/" + code + ".json")
          .then(function(r) { return r.ok ? r.json() : null; })
          .then(function(dict) {
            if (dict) { TRANSLATIONS[code] = dict; _doApplyLanguage(code, displayName, flagFile); }
            else { _doApplyLanguage("en", displayName, flagFile); }
          })
          .catch(function() { _doApplyLanguage("en", displayName, flagFile); });
      }
    }
  }

  function _doApplyLanguage(code, displayName, flagFile) {
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      if (!el.dataset.i18nOriginal) el.dataset.i18nOriginal = el.innerHTML;
      var key = el.getAttribute("data-i18n");
      var dict = TRANSLATIONS[code];
      el.innerHTML = (code === "pt-BR" || !dict || !dict[key]) ? el.dataset.i18nOriginal : dict[key];
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      if (!el.dataset.i18nPhOriginal) el.dataset.i18nPhOriginal = el.getAttribute("placeholder") || "";
      var key = el.getAttribute("data-i18n-placeholder");
      var dict = TRANSLATIONS[code];
      el.setAttribute("placeholder", (code === "pt-BR" || !dict || !dict[key]) ? el.dataset.i18nPhOriginal : dict[key]);
    });
    document.querySelectorAll("[data-i18n-aria]").forEach(function (el) {
      if (!el.dataset.i18nAriaOriginal) el.dataset.i18nAriaOriginal = el.getAttribute("aria-label") || "";
      var key = el.getAttribute("data-i18n-aria");
      var dict = TRANSLATIONS[code];
      el.setAttribute("aria-label", (code === "pt-BR" || !dict || !dict[key]) ? el.dataset.i18nAriaOriginal : dict[key]);
    });
    localStorage.setItem("site-lang", code);
    document.documentElement.lang = code;
    refreshLangPanelLabels();

    var lang = LANGUAGES.find(function (l) { return l.code === code; }) || LANGUAGES[0];
    var name = displayName || lang.native;
    var flagSrc = FLAG_DIR + (flagFile || lang.flag);

    if (displayName || flagFile) {
      localStorage.setItem("site-lang-display", JSON.stringify({ name: name, flag: flagFile || lang.flag }));
    } else {
      localStorage.removeItem("site-lang-display");
    }

    var flag2 = document.getElementById("rd-lang-flag-2");
    var name2 = document.getElementById("rd-lang-name-2");
    if (flag2) flag2.src = flagSrc;
    if (name2) name2.textContent = name;

    document.querySelectorAll(".rd-lang-menu button").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-code") === code);
    });
    document.querySelectorAll(".gh-lang-grid button, .gh-mobile-sub button").forEach(function (btn) {
      btn.classList.toggle("active-lang", btn.getAttribute("data-code") === code);
    });
  }

  function buildMenu(menuEl) {
    if (!menuEl) return;
    menuEl.innerHTML = LANGUAGES.map(function (l) {
      var soon = "";
      return (
        '<button type="button" data-code="' + l.code + '" class="' + (currentLang() === l.code ? "active" : "") + '">' +
        '<img class="rd-lang-flag" src="' + FLAG_DIR + l.flag + '" alt="" />' +
        "<span>" + l.native + "</span>" + soon +
        "</button>"
      );
    }).join("") +
      '<div class="rd-lang-note">Tradução ativa para 28 idiomas. Selecione seu país ou idioma — a interface se adapta automaticamente.</div>';

    menuEl.querySelectorAll("button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyLanguage(btn.getAttribute("data-code"));
        menuEl.classList.remove("open");
      });
    });
  }

  // Grid compacto (3 colunas) usado dentro dos mega-menus — mesmo padrão
  // visual dos demais mega-menus do cabeçalho.
  function buildGridMenu(gridEl, closeOnPick) {
    if (!gridEl) return;
    gridEl.innerHTML = LANGUAGES.map(function (l) {
      return (
        '<button type="button" data-code="' + l.code + '" class="' + (currentLang() === l.code ? "active-lang" : "") + '">' +
        '<img class="rd-lang-flag" src="' + FLAG_DIR + l.flag + '" alt="" />' +
        "<span>" + l.native + "</span>" +
        "</button>"
      );
    }).join("");
    gridEl.querySelectorAll("button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyLanguage(btn.getAttribute("data-code"));
        if (closeOnPick) {
          var mobileMenu = document.getElementById("gh-mobile-menu");
          var hamburger = document.getElementById("gh-hamburger-btn");
          if (mobileMenu) mobileMenu.classList.remove("open");
          if (hamburger) {
            hamburger.setAttribute("aria-expanded", "false");
            hamburger.innerHTML = '<i class="fa-solid fa-bars" aria-hidden="true"></i>';
          }
        }
      });
    });
  }

  // Mega-menu Idiomas: coluna 1 = regiões, coluna 2 = países da região ativa
  // (cada país tem bandeira e nome próprios, mesmo reaproveitando o dicionário
  // de outro idioma quando a tradução dedicada ainda não existe).
  function buildRegionMenu(regionListEl, gridEl) {
    if (!regionListEl || !gridEl) return;

    function findRegionOf(code) {
      for (var i = 0; i < REGIONS.length; i++) {
        if (REGIONS[i].codes.indexOf(code) !== -1) return REGIONS[i].id;
      }
      return REGIONS[0].id;
    }

    function renderCountries(regionId) {
      var list = COUNTRIES[regionId] || [];
      var saved = null;
      try { saved = JSON.parse(localStorage.getItem("site-lang-display") || "null"); } catch (e) {}

      gridEl.innerHTML = list.map(function (c) {
        var isActive = currentLang() === c.code && saved && saved.name === c.country;
        return (
          '<button type="button" data-code="' + c.code + '" data-country="' + c.country + '" data-flag="' + c.flag + '" class="' + (isActive ? "active-lang" : "") + '">' +
          '<img class="rd-lang-flag" src="' + FLAG_DIR + c.flag + '" alt="" />' +
          "<span>" + c.country + "</span>" +
          "</button>"
        );
      }).join("");
      gridEl.querySelectorAll("button").forEach(function (btn) {
        btn.addEventListener("click", function () {
          applyLanguage(btn.getAttribute("data-code"), btn.getAttribute("data-country"), btn.getAttribute("data-flag"));
          renderCountries(regionId);
        });
      });
    }

    regionListEl.innerHTML = REGIONS.map(function (r) {
      return '<button type="button" data-region="' + r.id + '">' + r.name + "</button>";
    }).join("");

    var activeRegion = findRegionOf(currentLang());
    regionListEl.querySelectorAll("button").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-region") === activeRegion);
      btn.addEventListener("click", function () {
        regionListEl.querySelectorAll("button").forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        renderCountries(btn.getAttribute("data-region"));
      });
    });

    renderCountries(activeRegion);
  }

  function wireToggle(toggleId, menuId, otherMenuId) {
    var toggle = document.getElementById(toggleId);
    var menu = document.getElementById(menuId);
    var other = document.getElementById(otherMenuId);
    if (!toggle || !menu) return;
    toggle.addEventListener("click", function (e) {
      e.stopPropagation();
      menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", menu.classList.contains("open"));
      if (other) other.classList.remove("open");
    });
  }

  var inited = false;
  function init() {
    if (inited) return;
    if (!document.getElementById("gh-region-list")) return;
    inited = true;
    // Seletor de idiomas centralizado no cabeçalho (mega-menu Idiomas) — o
    // rodapé não possui mais seletor próprio.

    // Cabeçalho: mega-menu "Idiomas" — coluna 1 região, coluna 2 países da região (abre no hover via CSS)
    buildRegionMenu(document.getElementById("gh-region-list"), document.getElementById("gh-lang-grid"));
    buildGridMenu(document.getElementById("gh-lang-grid-mobile"), true);
    var note = document.getElementById("gh-lang-note");
    if (note) note.textContent = "Tradução ativa para 28 idiomas e 195 países. Selecione seu país para localizar a interface.";

    var savedDisplay = null;
    try { savedDisplay = JSON.parse(localStorage.getItem("site-lang-display") || "null"); } catch (e) {}
    if (savedDisplay) {
      applyLanguage(currentLang(), savedDisplay.name, savedDisplay.flag);
    } else {
      applyLanguage(currentLang());
    }

    var yearEl = document.getElementById("rd-footer-year");
    if (yearEl) yearEl.textContent = new Date().getFullYear();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  document.addEventListener("partials:ready", init);
})();
