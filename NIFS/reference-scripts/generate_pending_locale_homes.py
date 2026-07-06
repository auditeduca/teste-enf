#!/usr/bin/env python3
"""Generate pending tier-3/base locale home_page.json files (2026.3.0)."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "datasets" / "content" / "site" / "home_page.json"
BY_LOCALE = ROOT / "datasets" / "by-locale"

# fmt: off
LOCALES: dict[str, dict[str, Any]] = {
    "cs-CZ": {
        "hero": ("Technologie a znalosti pro", "efektivnější a udržitelnější ošetřovatelství.",
                 "Klinické nástroje, protokoly, škály a vzdělávací obsah pro studenty, sestry, manažery a zdravotnická zařízení — s digitální odpovědností a měřitelným dopadem.",
                 "Zdravotní sestra v klinickém prostředí", "Prozkoumat nástroje", "O platformě",
                 [("195+", "Propojené země"), ("Stovky", "Ovlivněných profesionálů"), ("+100", "Digitálních nástrojů")]),
        "search": ("Co dnes potřebujete?", "Např.: Kapání, Bradenova škála, Inzulín, OŠP…", "Hledat"),
        "seo": ("Nursing Calculators | Globální platforma klinické inteligence",
                "Udržitelná technologie pro ošetřovatelství — nástroje, škály, vzdělávání a governance. 195+ zemí, Nursing Calculators 2026."),
        "profile": ("Přizpůsobte si zážitek", "Obsah, nástroje a ukazatele podle vašeho profesního profilu."),
        "feed": ("Klinické novinky", "Sledujte novinky platformy v reálném čase.", "Zobrazit vše", "Tip dne", "Více tipů"),
        "os": ("Ekosystém Calculadoras de Enfermagem", "Jak se propojují péče, management, vzdělávání a udržitelnost.", "Prozkoumat ekosystém",
               [("Péče", "Kalkulačky, škály a klinické protokoly."), ("Vzdělávání", "Články, kurzy, flashcards a simulace."),
                ("Management", "Ukazatele, kvalita a bezpečí pacientů."), ("Udržitelnost", "Digital-first technologie s měřitelným dopadem.")]),
        "kh": ("Aplikované znalosti", "Od článku k certifikaci: kontinuální klinická learning path.", "Začít cestu",
               ["Článek", "Flashcard", "Kvíz", "Klinický případ", "Certifikát"]),
        "cases": ("Klinické vzdělávání", "Interaktivní klinické případy podle specializace.", "Zobrazit všechny případy",
                  ["Dospělí", "Pediatrie", "JIP", "Urgentní", "Operační sál", "Rodinné zdraví"]),
        "comp": ("Můj rozvoj", "Hodnoťte a rozvíjejte své profesní kompetence.", ["Technická", "Vědecká", "Management", "Leadership", "Bezpečí pacientů", "Udržitelnost"],
                 "Provést úvodní hodnocení", "Zobrazit mou cestu"),
        "ai": ("Klinický asistent", "Umělá inteligence s lidským dohledem pro ošetřovatelskou praxi.",
               ["Odpovídá na klinické dotazy", "Navrhuje personalizovaný obsah", "Sestaví studijní plán", "Vysvětluje protokoly", "Generuje simulace"],
               "Odpovědi AI nenahrazují profesionální klinické rozhodnutí.", "Mluvit s asistentem"),
        "safety": ("Centrum bezpečí pacientů", "Mezinárodní cíle, nežádoucí události a bezpečnostní protokoly.", "Přejít do centra bezpečí",
                   ["Mezinárodní cíle bezpečí pacientů (IPSG)", "Nežádoucí události", "Téměř incident", "Hlášení", "Bezpečnostní protokoly"]),
        "occ": ("Pracovní zdraví v ošetřovatelství", "Řízení rizik a pohoda zdravotnických pracovníků.", "Přejít na pracovní zdraví"),
        "impact": ("Dopad platformy", "Čísla odrážející skutečné využití sestrami.",
                   ["Provedené výpočty", "Přístupy k protokolům", "Použité rozhodovací stromy", "Dokončené simulace", "Zaznamenané hodiny studia"]),
        "sust": ("Digitální udržitelnost", "Digital-first technologie s měřitelným environmentálním dopadem.", "Zjistit více o udržitelnosti",
                 ["Ušetřené listy papíru", "Snížení CO₂ (kg)", "100% digitální protokoly"]),
        "gov": ("Governance a transparentnost", "Důvěra založená na soukromí, přístupnosti a digitální odpovědnosti.", "Přejít do centra governance",
                ["Soukromí a LGPD", "Cookies", "Odpovědná AI", "Udržitelnost", "Přístupnost", "Vědecká metodologie"],
                "Vědecká důvěryhodnost", "Obsah recenzovaný odborníky, transparentní metodologie.",
                ["Redakční rada", "Spolupracující odborníci", "Proces recenze"], "Partneři a instituce", ["Univerzity", "Nemocnice", "Vědecké společnosti"]),
        "cta": ("Připraveni povýšit svou ošetřovatelskou praxi?", "Připojte se k profesionálům ve 195+ zemích.",
                "Vytvořit bezplatný účet", "Prozkoumat nástroje"),
        "profiles": [
            ("estudante", "Jsem student", "Studijní trasy, flashcards a simulace.", "graduation-cap"),
            ("profissional", "Jsem klinická sestra", "Kalkulačky, škály a protokoly pro praxi.", "user-check"),
            ("profissional", "Jsem urgentní sestra", "Rychlé nástroje pro složité situace.", "siren"),
            ("gestor", "Jsem manažer", "Ukazatele, kvalita a řízení týmů.", "chart"),
            ("academico", "Jsem pedagog", "Didaktické zdroje a databáze otázek.", "book"),
            ("gestor", "Jsem instituce", "Firemní řešení, compliance a škálování.", "building"),
        ],
        "featured": [
            ("Kalkulačka kapání", "Bezpečný výpočet kapek za minutu.", "TOOL.INFUSION", "Použít"),
            ("Bradenova škála", "Hodnocení rizika dekubitů.", "TOOL.BRADEN", "Aplikovat"),
            ("Kalkulačka BMI", "Hodnocení indexu tělesné hmotnosti.", "TOOL.BMI", "Použít"),
            ("Vodní bilance", "Sledování příjmu a výdeje tekutin.", None, "Použít"),
        ],
    },
    "pl-PL": {
        "hero": ("Technologia i wiedza dla", "bardziej efektywnej i zrównoważonej pielęgniarstwa.",
                 "Narzędzia kliniczne, protokoły, skale i treści edukacyjne dla studentów, pielęgniarek, managerów i placówek zdrowia — z cyfrową odpowiedzialnością i mierzalnym wpływem.",
                 "Pielęgniarka w środowisku klinicznym", "Poznaj narzędzia", "O platformie",
                 [("195+", "Połączone kraje"), ("Setki", "Profesjonalistów"), ("+100", "Narzędzi cyfrowych")]),
        "search": ("Czego potrzebujesz dziś?", "Np.: Kroplówka, Skala Bradena, Insulina, OPK…", "Szukaj"),
        "seo": ("Nursing Calculators | Globalna platforma inteligencji klinicznej",
                "Zrównoważona technologia dla pielęgniarstwa — narzędzia, skale, edukacja i governance. 195+ krajów."),
        "profile": ("Spersonalizuj swoje doświadczenie", "Treści, narzędzia i wskaźniki dopasowane do profilu zawodowego."),
        "feed": ("Aktualizacje kliniczne", "Śledź nowości platformy w czasie rzeczywistym.", "Zobacz wszystkie", "Porada dnia", "Więcej porad"),
        "os": ("Ekosystem Calculadoras de Enfermagem", "Jak łączą się opieka, zarządzanie, edukacja i zrównoważony rozwój.", "Poznaj ekosystem",
               [("Opieka", "Kalkulatory, skale i protokoły kliniczne."), ("Edukacja", "Artykuły, kursy, fiszki i symulacje."),
                ("Zarządzanie", "Wskaźniki, jakość i bezpieczeństwo pacjenta."), ("Zrównoważony rozwój", "Technologia digital first.")]),
        "kh": ("Wiedza stosowana", "Od artykułu do certyfikatu: ciągła ścieżka uczenia klinicznego.", "Rozpocznij ścieżkę",
               ["Artykuł", "Fiszka", "Quiz", "Przypadek kliniczny", "Certyfikat"]),
        "cases": ("Szkolenie kliniczne", "Interaktywne przypadki kliniczne według specjalizacji.", "Zobacz wszystkie przypadki",
                  ["Dorośli", "Pediatria", "OIOM", "Ratunkowa", "Blok operacyjny", "Zdrowie rodziny"]),
        "comp": ("Mój rozwój", "Oceniaj i rozwijaj kompetencje zawodowe.", ["Techniczna", "Naukowa", "Zarządzanie", "Przywództwo", "Bezpieczeństwo pacjenta", "Zrównoważony rozwój"],
                 "Wykonaj ocenę wstępną", "Zobacz moją ścieżkę"),
        "ai": ("Asystent kliniczny", "Sztuczna inteligencja z nadzorem człowieka dla praktyki pielęgniarskiej.",
               ["Odpowiada na pytania kliniczne", "Sugeruje spersonalizowane treści", "Tworzy plan nauki", "Wyjaśnia protokoły", "Generuje symulacje"],
               "Odpowiedzi AI nie zastępują profesjonalnej decyzji klinicznej.", "Porozmawiaj z asystentem"),
        "safety": ("Centrum bezpieczeństwa pacjenta", "Cele międzynarodowe, zdarzenia niepożądane i protokoły.", "Przejdź do centrum",
                   ["Międzynarodowe Cele Bezpieczeństwa Pacjenta (IPSG)", "Zdarzenia niepożądane", "Zdarzenie potencjalnie szkodliwe", "Zgłoszenia", "Protokoły bezpieczeństwa"]),
        "occ": ("Zdrowie zawodowe w pielęgniarstwie", "Zarządzanie ryzykiem i dobrostan pracowników.", "Przejdź do BHP"),
        "impact": ("Wpływ platformy", "Liczby odzwierciedlające rzeczywiste użycie.", ["Wykonane obliczenia", "Otwarte protokoły", "Użyte drzewa decyzyjne", "Ukończone symulacje", "Godziny nauki"]),
        "sust": ("Zrównoważony rozwój cyfrowy", "Technologia digital first z mierzalnym wpływem.", "Poznaj naszą zrównoważoność", ["Zaoszczędzone kartki", "Redukcja CO₂ (kg)", "100% cyfrowe protokoły"]),
        "gov": ("Governance i transparentność", "Zaufanie oparte na prywatności i dostępności.", "Centrum governance",
                ["Prywatność i LGPD", "Cookies", "Odpowiedzialna AI", "Zrównoważony rozwój", "Dostępność", "Metodologia naukowa"],
                "Wiarygodność naukowa", "Treści recenzowane przez specjalistów.", ["Rada redakcyjna", "Współpracujący specjaliści", "Proces recenzji"], "Partnerzy", ["Uniwersytety", "Szpitale", "Towarzystwa naukowe"]),
        "cta": ("Gotowy podnieść swoją praktykę?", "Dołącz do profesjonalistów w 195+ krajach.", "Utwórz darmowe konto", "Poznaj narzędzia"),
        "profiles": [
            ("estudante", "Jestem studentem", "Ścieżki, fiszki i symulacje.", "graduation-cap"),
            ("profissional", "Jestem pielęgniarką kliniczną", "Kalkulatory i protokoły.", "user-check"),
            ("profissional", "Jestem pielęgniarką ratunkową", "Szybkie narzędzia.", "siren"),
            ("gestor", "Jestem managerem", "Wskaźniki i jakość.", "chart"),
            ("academico", "Jestem wykładowcą", "Zasoby dydaktyczne.", "book"),
            ("gestor", "Jestem instytucją", "Rozwiązania korporacyjne.", "building"),
        ],
        "featured": [
            ("Kalkulator kroplówki", "Bezpieczny przepływ kropli/min.", "TOOL.INFUSION", "Użyj"),
            ("Skala Bradena", "Ryzyko odleżyn.", "TOOL.BRADEN", "Zastosuj"),
            ("Kalkulator BMI", "Indeks masy ciała.", "TOOL.BMI", "Użyj"),
            ("Bilans wodny", "Kontrola płynów.", None, "Użyj"),
        ],
    },
    "nl-NL": {
        "hero": ("Technologie en kennis voor", "efficiëntere en duurzamere verpleegkunde.",
                 "Klinische tools, protocollen, schalen en educatieve content voor studenten, verpleegkundigen, managers en zorginstellingen.",
                 "Verpleegkundige in klinische omgeving", "Tools verkennen", "Over het platform",
                 [("195+", "Landen verbonden"), ("Honderden", "Professionals"), ("+100", "Digitale tools")]),
        "search": ("Wat heeft u vandaag nodig?", "Bijv.: Druppelsnelheid, Braden, Insuline…", "Zoeken"),
        "seo": ("Nursing Calculators | Globaal platform voor klinische intelligentie", "Duurzame technologie voor verpleegkunde. 195+ landen."),
        "profile": ("Personaliseer uw ervaring", "Content, tools en indicatoren op maat."),
        "feed": ("Klinische updates", "Volg platformnieuws in realtime.", "Alle updates", "Tip van de dag", "Meer tips"),
        "os": ("Calculadoras de Enfermagem-ecosysteem", "Hoe zorg, management, educatie en duurzaamheid samenkomen.", "Ecosysteem verkennen",
               [("Zorg", "Calculators, schalen en protocollen."), ("Educatie", "Artikelen, cursussen en simulaties."),
                ("Management", "Indicatoren en patiëntveiligheid."), ("Duurzaamheid", "Digital-first technologie.")]),
        "kh": ("Toegepaste kennis", "Van artikel tot certificaat.", "Start traject",
               ["Artikel", "Flashcard", "Quiz", "Klinische casus", "Certificaat"]),
        "cases": ("Klinische training", "Interactieve casussen per specialisme.", "Alle casussen",
                  ["Volwassenen", "Pediatrie", "IC", "Spoedeisende hulp", "OK", "Gezinszorg"]),
        "comp": ("Mijn ontwikkeling", "Beoordeel en ontwikkel competenties.", ["Technisch", "Wetenschappelijk", "Management", "Leiderschap", "Patiëntveiligheid", "Duurzaamheid"],
                 "Start assessment", "Mijn traject"),
        "ai": ("Klinische assistent", "AI met menselijk toezicht.", ["Beantwoordt klinische vragen", "Personaliseert content", "Studieplan", "Legt protocollen uit", "Genereert simulaties"],
               "AI vervangt geen klinisch oordeel.", "Praat met assistent"),
        "safety": ("Centrum patiëntveiligheid", "Internationale doelen en protocollen.", "Naar veiligheidscentrum",
                   ["Internationale Patiëntveiligheidsdoelen (IPSG)", "Ongevallen", "Bijna-incident", "Meldingen", "Veiligheidsprotocollen"]),
        "occ": ("Arbeidsgezondheid", "Risicobeheer en welzijn.", "Naar arbeidsgezondheid"),
        "impact": ("Platformimpact", "Cijfers van echt gebruik.", ["Berekeningen", "Protocollen", "Beslisbomen", "Simulaties", "Studie-uren"]),
        "sust": ("Digitale duurzaamheid", "Digital first met meetbare impact.", "Onze duurzaamheid", ["Papier bespaard", "CO₂ reductie (kg)", "100% digitaal"]),
        "gov": ("Governance en transparantie", "Vertrouwen via privacy en toegankelijkheid.", "Governancecentrum",
                ["Privacy en LGPD", "Cookies", "Verantwoorde AI", "Duurzaamheid", "Toegankelijkheid", "Methodologie"],
                "Wetenschappelijke geloofwaardigheid", "Content beoordeeld door experts.", ["Redactieraad", "Specialisten", "Reviewproces"], "Partners", ["Universiteiten", "Ziekenhuizen", "Verenigingen"]),
        "cta": ("Klaar om uw praktijk te verbeteren?", "Sluit u aan bij professionals in 195+ landen.", "Gratis account", "Tools verkennen"),
        "profiles": [
            ("estudante", "Ik ben student", "Leertrajecten en flashcards.", "graduation-cap"),
            ("profissional", "Ik ben verpleegkundige", "Calculators en protocollen.", "user-check"),
            ("profissional", "Spoedeisende hulp", "Snelle tools.", "siren"),
            ("gestor", "Ik ben manager", "Indicatoren en kwaliteit.", "chart"),
            ("academico", "Ik ben docent", "Didactische bronnen.", "book"),
            ("gestor", "Ik ben instelling", "Enterprise-oplossingen.", "building"),
        ],
        "featured": [
            ("Druppelsnelheid", "Veilig druppels/min.", "TOOL.INFUSION", "Gebruik"),
            ("Braden-schaal", "Decubitusrisico.", "TOOL.BRADEN", "Toepas"),
            ("BMI-calculator", "Body mass index.", "TOOL.BMI", "Gebruik"),
            ("Vochtbalans", "In- en output.", None, "Gebruik"),
        ],
    },
    "ar": {
        "hero": ("التكنولوجيا والمعرفة من أجل", "تمريض أكثر كفاءة واستدامة.",
                 "أدوات سريرية وبروتوكولات ومقاييس ومحتوى تعليمي للطلاب والممرضين والمديرين ومؤسسات الرعاية الصحية — بمسؤولية رقمية وأثر قابل للقياس.",
                 "ممرض في بيئة سريرية", "استكشاف الأدوات", "تعرّف على المنصة",
                 [("195+", "دول متصلة"), ("مئات", "مهنيين"), ("+100", "أدوات رقمية")]),
        "search": ("ماذا تحتاج اليوم؟", "مثال: التسريب، مقياس برaden، الأنسولين…", "بحث"),
        "seo": ("Nursing Calculators | منصة عالمية للذكاء السريري", "تكنولوجيا مستدامة للتمريض — أدوات ومقاييس وتعليم. 195+ دولة."),
        "profile": ("خصّص تجربتك", "محتوى وأدوات ومؤشرات حسب ملفك المهني."),
        "feed": ("تحديثات سريرية", "تابع أخبار المنصة في الوقت الفعلي.", "عرض الكل", "نصيحة اليوم", "المزيد"),
        "os": ("نظام Calculadoras de Enfermagem", "كيف تتصل الرعاية والإدارة والتعليم والاستدامة.", "استكشاف النظام",
               [("الرعاية", "حاسبات ومقاييس وبروتوكols."), ("التعليم", "مقالات ودورات وبطاقات."), ("الإدارة", "مؤشرات وجودة وسلامة."), ("الاستدامة", "تقنية digital first.")]),
        "kh": ("معرفة تطبيقية", "من المقال إلى الشهادة.", "ابدأ المسار", ["مقال", "بطاقة", "اختبار", "حالة سريرية", "شهادة"]),
        "cases": ("تدريب سريري", "حالات تفاعلية حسب التخصص.", "كل الحالات", ["بالغين", "أطفال", "عناية مركزة", "طوارئ", "عمليات", "صحة الأسرة"]),
        "comp": ("تطوري", "قيّم وطوّر كفاءاتك.", ["تقنية", "علمية", "إدارة", "قيادة", "سلامة المريض", "استدامة"], "تقييم أولي", "مساري"),
        "ai": ("مساعد سريري", "ذكاء اصطناعي بإشراف بشري.", ["يجيب على الأسئلة", "محتوى مخصص", "خطة دراسة", "شرح البروتوكولات", "محاكاة"], "الذكاء الاصطناعي لا يغني عن القرار السريري.", "تحدث مع المساعد"),
        "safety": ("مركز سلامة المريض", "أهداف دولية وأحداث وسلامة.", "المركز", ["أهداف IPSG", "أحداث ضارة", "شبه حادث", "إبلاغ", "بروتوكولات"]),
        "occ": ("الصحة المهنية", "إدارة المخاطر ورفاهية العاملين.", "الصحة المهنية"),
        "impact": ("أثر المنصة", "أرقام الاستخدام الفعلي.", ["حسابات", "بروتوكولات", "أشجار قرار", "محاكاة", "ساعات دراسة"]),
        "sust": ("استدامة رقمية", "تقنية digital first.", "استدامتنا", ["ورق موفر", "CO₂ (kg)", "100% رقمي"]),
        "gov": ("حوكمة وشفافية", "ثقة عبر الخصوصية.", "مركز الحوكمة", ["خصوصية LGPD", "Cookies", "AI مسؤول", "استدامة", "إتاحة", "منهجية"], "مصداقية علمية", "محتوى مراجع.", ["تحرير", "متخصصون", "مراجعة"], "شركاء", ["جامعات", "مستشفيات", "جمعيات"]),
        "cta": ("مستعد لتطوير ممارستك؟", "انضم لمهنيين في 195+ دولة.", "حساب مجاني", "استكشاف الأدوات"),
        "profiles": [("estudante", "طالب", "مسارات ومحاكاة.", "graduation-cap"), ("profissional", "ممرض سريري", "حاسبات وبروتوكولات.", "user-check"), ("profissional", "طوارئ", "أدوات سريعة.", "siren"), ("gestor", "مدير", "مؤشرات.", "chart"), ("academico", "مدرس", "موارد.", "book"), ("gestor", "مؤسسة", "حلول.", "building")],
        "featured": [("حاسبة التسريب", "قطرات/دقيقة.", "TOOL.INFUSION", "استخدم"), ("مقياس Braden", "قرحة.", "TOOL.BRADEN", "طبّق"), ("BMI", "كتلة الجسم.", "TOOL.BMI", "استخدم"), ("توازن سوائل", "سوائل.", None, "استخدم")],
        "featured_title": "الأدوات الأكثر استخداماً", "featured_all": "عرض الكل",
    },
    "ru-RU": {
        "hero": ("Технологии и знания для", "более эффективного и устойчивого сестринского дела.",
                 "Клинические инструменты, протоколы, шкалы и образовательный контент для студентов, медсестёр, менеджеров и учреждений.",
                 "Медсестра в клинической среде", "Инструменты", "О платформе",
                 [("195+", "Стран"), ("Сотни", "Специалистов"), ("+100", "Инструментов")]),
        "search": ("Что вам нужно сегодня?", "Напр.: Капельница, Braden, Инсулин…", "Поиск"),
        "seo": ("Nursing Calculators | Глобальная платформа", "Устойчивые технологии для сестринского дела. 195+ стран."),
        "profile": ("Персонализируйте опыт", "Контент и инструменты по профилю."),
        "feed": ("Клинические обновления", "Новости платформы.", "Все", "Совет дня", "Ещё"),
        "os": ("Экосистема Calculadoras de Enfermagem", "Связь помощи, управления, образования.", "Экосистема",
               [("Помощь", "Калькуляторы и протоколы."), ("Образование", "Статьи и симуляции."), ("Управление", "Показатели."), ("Устойчивость", "Digital first.")]),
        "kh": ("Прикладные знания", "От статьи до сертификата.", "Начать", ["Статья", "Карточка", "Тест", "Случай", "Сертификат"]),
        "cases": ("Клиническое обучение", "Интерактивные случаи.", "Все случаи", ["Взрослые", "Педиатрия", "Реанимация", "Неотложная", "Операционная", "Семья"]),
        "comp": ("Моё развитие", "Компетенции.", ["Техн.", "Науч.", "Управ.", "Лидер.", "Безопасность", "Устойч."], "Оценка", "Мой путь"),
        "ai": ("Клинический ассистент", "ИИ с человеческим контролем.", ["Ответы", "Контент", "План", "Протоколы", "Симуляции"], "ИИ не заменяет решение.", "Ассистент"),
        "safety": ("Центр безопасности", "IPSG и протоколы.", "Центр", ["IPSG", "События", "Почти инцидент", "Уведомления", "Протоколы"]),
        "occ": ("Охрана труда", "Риски и благополучие.", "Охрана труда"),
        "impact": ("Влияние", "Реальное использование.", ["Расчёты", "Протоколы", "Деревья", "Симуляции", "Часы"]),
        "sust": ("Цифровая устойчивость", "Digital first.", "Устойчивость", ["Бумага", "CO₂", "100% цифра"]),
        "gov": ("Управление", "Доверие.", "Governance", ["LGPD", "Cookies", "ИИ", "Устойч.", "Доступ.", "Метод."], "Достоверность", "Рецензии.", ["Редакция", "Эксперты", "Review"], "Партнёры", ["ВУЗы", "Больницы", "Общества"]),
        "cta": ("Готовы улучшить практику?", "195+ стран.", "Аккаунт", "Инструменты"),
        "profiles": [("estudante", "Студент", "Обучение.", "graduation-cap"), ("profissional", "Медсестра", "Практика.", "user-check"), ("profissional", "Неотложка", "Быстро.", "siren"), ("gestor", "Менеджер", "KPI.", "chart"), ("academico", "Препод.", "Ресурсы.", "book"), ("gestor", "Институция", "B2B.", "building")],
        "featured": [("Капельница", "Кап/мин.", "TOOL.INFUSION", "Исп."), ("Braden", "Пролежни.", "TOOL.BRADEN", "Примен."), ("ИМТ", "BMI.", "TOOL.BMI", "Исп."), ("Баланс", "Жидк.", None, "Исп.")],
        "featured_title": "Популярные инструменты", "featured_all": "Все",
    },
    "ko-KR": {
        "hero": ("더 효율적이고 지속 가능한", "간호를 위한 기술과 지식.",
                 "학생, 간호사, 관리자 및 의료기관을 위한 임상 도구, 프로토콜, 척도 및 교육 콘텐츠.",
                 "임상 환경의 간호사", "도구 탐색", "플랫폼 소개",
                 [("195+", "연결된 국가"), ("수백", "전문가"), ("+100", "디지털 도구")]),
        "search": ("오늘 무엇이 필요하신가요?", "예: 드립, Braden, 인슐린…", "검색"),
        "seo": ("Nursing Calculators | 글로벌 임상 인텔리전스", "지속 가능한 간호 기술. 195+ 국가."),
        "profile": ("경험 맞춤 설정", "프로필에 맞는 콘텐츠와 도구."),
        "feed": ("임상 업데이트", "실시간 플랫폼 소식.", "전체 보기", "오늘의 팁", "더 보기"),
        "os": ("Calculadoras de Enfermagem 생태계", "돌봄·관리·교육·지속가능성 연결.", "생태계 탐색",
               [("돌봄", "계산기·프로토콜."), ("교육", "기사·시뮬레이션."), ("관리", "지표·품질."), ("지속가능성", "Digital first.")]),
        "kh": ("응용 지식", "기사에서 인증까지.", "시작", ["기사", "플ashcard", "퀴즈", "증례", "인증"]),
        "cases": ("임상 훈련", "전문분야별 증례.", "전체", ["성인", "소아", "중환자", "응급", "수술", "가정"]),
        "comp": ("내 성장", "역량 개발.", ["기술", "과학", "관리", "리더십", "환자안전", "지속가능"], "초기 평가", "내 경로"),
        "ai": ("임상 어시스턴트", "인간 감독 AI.", ["임상 Q&A", "맞춤 콘텐츠", "학습 계획", "프로토콜", "시뮬레이션"], "AI는 임상 판단 대체 불가.", "대화"),
        "safety": ("환자안전 센터", "IPSG·프로토콜.", "센터", ["IPSG", "이상사례", "근접오류", "알림", "프로토콜"]),
        "occ": ("산업보건", "위험·웰빙.", "산업보건"),
        "impact": ("플랫폼 영향", "실사용 지표.", ["계산", "프로토콜", "의사결정", "시뮬", "학습시간"]),
        "sust": ("디지털 지속가능", "Digital first.", "지속가능성", ["종이", "CO₂", "100% 디지털"]),
        "gov": ("거버넌스", "신뢰.", "센터", ["LGPD", "Cookies", "AI", "지속", "접근성", "방법론"], "과학적 신뢰", "전문가 검토.", ["편집", "전문가", "리뷰"], "파트너", ["대학", "병원", "학회"]),
        "cta": ("간호 실무를 높일 준비?", "195+ 국가.", "무료 계정", "도구"),
        "profiles": [("estudante", "학생", "학습.", "graduation-cap"), ("profissional", "간호사", "임상.", "user-check"), ("profissional", "응급", "신속.", "siren"), ("gestor", "관리자", "KPI.", "chart"), ("academico", "교수", "자료.", "book"), ("gestor", "기관", "B2B.", "building")],
        "featured": [("드립 계산", "방/min.", "TOOL.INFUSION", "사용"), ("Braden", "욕창.", "TOOL.BRADEN", "적용"), ("BMI", "체질량.", "TOOL.BMI", "사용"), ("수분", "균형.", None, "사용")],
        "featured_title": "가장 많이 쓰는 도구", "featured_all": "전체",
    },
    "tr-TR": {
        "hero": ("Daha verimli ve sürdürülebilir", "hemşirelik için teknoloji ve bilgi.",
                 "Öğrenciler, hemşireler, yöneticiler ve kurumlar için klinik araçlar, protokoller ve eğitim içeriği.",
                 "Klinik ortamda hemşire", "Araçları keşfet", "Platform hakkında",
                 [("195+", "Ülke"), ("Yüzlerce", "Profesyonel"), ("+100", "Dijital araç")]),
        "search": ("Bugün neye ihtiyacınız var?", "Örn.: Drip, Braden, İnsülin…", "Ara"),
        "seo": ("Nursing Calculators | Küresel klinik zeka", "Sürdürülebilir hemşirelik teknolojisi."),
        "profile": ("Deneyiminizi kişiselleştirin", "Profile göre içerik ve araçlar."),
        "feed": ("Klinik güncellemeler", "Platform haberleri.", "Tümü", "Günün ipucu", "Daha fazla"),
        "os": ("Calculadoras de Enfermagem ekosistemi", "Bakım, yönetim, eğitim bağlantısı.", "Keşfet",
               [("Bakım", "Hesaplayıcılar."), ("Eğitim", "Makaleler."), ("Yönetim", "Göstergeler."), ("Sürdürülebilirlik", "Digital first.")]),
        "kh": ("Uygulamalı bilgi", "Makaleden sertifikaya.", "Başla", ["Makale", "Flashcard", "Quiz", "Vaka", "Sertifika"]),
        "cases": ("Klinik eğitim", "İnteraktif vakalar.", "Tümü", ["Yetişkin", "Pediatri", "Yoğun", "Acil", "Ameliyat", "Aile"]),
        "comp": ("Gelişimim", "Yetkinlikler.", ["Teknik", "Bilim", "Yönetim", "Liderlik", "Güvenlik", "Sürd."], "Değerlendirme", "Yolum"),
        "ai": ("Klinik asistan", "İnsan denetimli AI.", ["Sorular", "İçerik", "Plan", "Protokol", "Simülasyon"], "AI karar yerine geçmez.", "Konuş"),
        "safety": ("Hasta güvenliği", "IPSG.", "Merkez", ["IPSG", "Olaylar", "Ramak kala", "Bildirim", "Protokol"]),
        "occ": ("İş sağlığı", "Risk yönetimi.", "İş sağlığı"),
        "impact": ("Platform etkisi", "Gerçek kullanım.", ["Hesap", "Protokol", "Karar", "Simül", "Saat"]),
        "sust": ("Dijital sürdürülebilirlik", "Digital first.", "Sürdürülebilirlik", ["Kağıt", "CO₂", "100% dijital"]),
        "gov": ("Yönetişim", "Güven.", "Merkez", ["LGPD", "Cookies", "AI", "Sürd.", "Erişim", "Metod"], "Bilimsel güven", "Uzman incelemesi.", ["Editör", "Uzman", "Review"], "Ortaklar", ["Üni.", "Hastane", "Dernek"]),
        "cta": ("Pratiğinizi yükseltmeye hazır mısınız?", "195+ ülke.", "Ücretsiz hesap", "Araçlar"),
        "profiles": [("estudante", "Öğrenci", "Eğitim.", "graduation-cap"), ("profissional", "Hemşire", "Klinik.", "user-check"), ("profissional", "Acil", "Hızlı.", "siren"), ("gestor", "Yönetici", "KPI.", "chart"), ("academico", "Öğretmen", "Kaynak.", "book"), ("gestor", "Kurum", "B2B.", "building")],
        "featured": [("Drip", "Damla/dk.", "TOOL.INFUSION", "Kullan"), ("Braden", "Yara.", "TOOL.BRADEN", "Uygula"), ("BMI", "VKİ.", "TOOL.BMI", "Kullan"), ("Sıvı", "Denge.", None, "Kullan")],
        "featured_title": "En çok kullanılan", "featured_all": "Tümü",
    },
    "id-ID": {
        "hero": ("Teknologi dan pengetahuan untuk", "keperawatan yang lebih efisien dan berkelanjutan.",
                 "Alat klinis, protokol, skala, dan konten edukasi untuk mahasiswa, perawat, manajer, dan institusi.",
                 "Perawat di lingkungan klinis", "Jelajahi alat", "Tentang platform",
                 [("195+", "Negara"), ("Ratusan", "Profesional"), ("+100", "Alat digital")]),
        "search": ("Apa yang Anda butuhkan hari ini?", "Contoh: Drip, Braden, Insulin…", "Cari"),
        "seo": ("Nursing Calculators | Platform intelijen klinis global", "Teknologi berkelanjutan untuk keperawatan."),
        "profile": ("Personalisasi pengalaman", "Konten sesuai profil profesional."),
        "feed": ("Pembaruan klinis", "Berita platform real-time.", "Semua", "Tips hari ini", "Lainnya"),
        "os": ("Ekosistem Calculadoras de Enfermagem", "Perawatan, manajemen, edukasi.", "Jelajahi",
               [("Perawatan", "Kalkulator."), ("Edukasi", "Artikel."), ("Manajemen", "Indikator."), ("Keberlanjutan", "Digital first.")]),
        "kh": ("Pengetahuan terapan", "Artikel ke sertifikasi.", "Mulai", ["Artikel", "Flashcard", "Kuis", "Kasus", "Sertifikat"]),
        "cases": ("Pelatihan klinis", "Kasus interaktif.", "Semua", ["Dewasa", "Pediatri", "ICU", "Gawat", "OK", "Keluarga"]),
        "comp": ("Perkembangan saya", "Kompetensi.", ["Teknis", "Ilmiah", "Manajemen", "Kepemimpinan", "Keselamatan", "Keberlanjutan"], "Assesmen awal", "Jalur saya"),
        "ai": ("Asisten klinis", "AI dengan supervisi manusia.", ["Jawab klinis", "Konten", "Rencana", "Protokol", "Simulasi"], "AI bukan pengganti keputusan klinis.", "Bicara"),
        "safety": ("Pusat keselamatan pasien", "IPSG.", "Pusat", ["IPSG", "Kejadian", "Near miss", "Notifikasi", "Protokol"]),
        "occ": ("Kesehatan kerja", "Manajemen risiko.", "Kesehatan kerja"),
        "impact": ("Dampak platform", "Penggunaan nyata.", ["Hitung", "Protokol", "Keputusan", "Simulasi", "Jam belajar"]),
        "sust": ("Keberlanjutan digital", "Digital first.", "Keberlanjutan", ["Kertas", "CO₂", "100% digital"]),
        "gov": ("Tata kelola", "Kepercayaan.", "Pusat", ["LGPD", "Cookies", "AI", "Keberlanjutan", "Akses", "Metode"], "Kredibilitas", "Review ahli.", ["Editorial", "Ahli", "Review"], "Mitra", ["Univ.", "RS", "Asosiasi"]),
        "cta": ("Siap meningkatkan praktik?", "195+ negara.", "Akun gratis", "Alat"),
        "profiles": [("estudante", "Mahasiswa", "Belajar.", "graduation-cap"), ("profissional", "Perawat", "Klinis.", "user-check"), ("profissional", "Gawat", "Cepat.", "siren"), ("gestor", "Manajer", "KPI.", "chart"), ("academico", "Dosen", "Materi.", "book"), ("gestor", "Institusi", "B2B.", "building")],
        "featured": [("Drip", "Tetes/mnt.", "TOOL.INFUSION", "Gunakan"), ("Braden", "Dekubitus.", "TOOL.BRADEN", "Terapkan"), ("BMI", "IMT.", "TOOL.BMI", "Gunakan"), ("Cairan", "Balance.", None, "Gunakan")],
        "featured_title": "Alat paling populer", "featured_all": "Semua",
    },
    "vi-VN": {
        "hero": ("Công nghệ và tri thức cho", "điều dưỡng hiệu quả và bền vững hơn.",
                 "Công cụ lâm sàng, giao thức, thang đo và nội dung giáo dục cho sinh viên, điều dưỡng và cơ sở y tế.",
                 "Điều dưỡng viên tại môi trường lâm sàng", "Khám phá công cụ", "Về nền tảng",
                 [("195+", "Quốc gia"), ("Hàng trăm", "Chuyên gia"), ("+100", "Công cụ số")]),
        "search": ("Hôm nay bạn cần gì?", "VD: Truyền dịch, Braden, Insulin…", "Tìm"),
        "seo": ("Nursing Calculators | Nền tảng trí tuệ lâm sàng toàn cầu", "Công nghệ bền vững cho điều dưỡng."),
        "profile": ("Cá nhân hóa trải nghiệm", "Nội dung theo hồ sơ nghề nghiệp."),
        "feed": ("Cập nhật lâm sàng", "Tin nền tảng thời gian thực.", "Tất cả", "Mẹo ngày", "Thêm"),
        "os": ("Hệ sinh thái Calculadoras de Enfermagem", "Chăm sóc, quản lý, giáo dục.", "Khám phá",
               [("Chăm sóc", "Máy tính."), ("Giáo dục", "Bài viết."), ("Quản lý", "Chỉ số."), ("Bền vững", "Digital first.")]),
        "kh": ("Tri thức ứng dụng", "Bài viết đến chứng chỉ.", "Bắt đầu", ["Bài", "Flashcard", "Quiz", "Ca lâm sàng", "Chứng chỉ"]),
        "cases": ("Đào tạo lâm sàng", "Ca tương tác.", "Tất cả", ["Người lớn", "Nhi", "ICU", "Cấp cứu", "Mổ", "Gia đình"]),
        "comp": ("Phát triển", "Năng lực.", ["Kỹ thuật", "Khoa học", "Quản lý", "Lãnh đạo", "An toàn", "Bền vững"], "Đánh giá", "Lộ trình"),
        "ai": ("Trợ lý lâm sàng", "AI có giám sát.", ["Hỏi đáp", "Nội dung", "Kế hoạch", "Giao thức", "Mô phỏng"], "AI không thay quyết định lâm sàng.", "Trò chuyện"),
        "safety": ("Trung tâm an toàn", "IPSG.", "Trung tâm", ["IPSG", "Sự cố", "Gần sự cố", "Thông báo", "Giao thức"]),
        "occ": ("Sức khỏe nghề nghiệp", "Quản lý rủi ro.", "Sức khỏe NN"),
        "impact": ("Tác động", "Sử dụng thực.", ["Tính toán", "Giao thức", "Quyết định", "Mô phỏng", "Giờ học"]),
        "sust": ("Bền vững số", "Digital first.", "Bền vững", ["Giấy", "CO₂", "100% số"]),
        "gov": ("Quản trị", "Tin cậy.", "Trung tâm", ["LGPD", "Cookies", "AI", "Bền vững", "Tiếp cận", "Phương pháp"], "Uy tín", "Chuyên gia.", ["Biên tập", "Chuyên gia", "Review"], "Đối tác", ["ĐH", "BV", "Hiệp hội"]),
        "cta": ("Sẵn sàng nâng tầm thực hành?", "195+ quốc gia.", "Tài khoản miễn phí", "Công cụ"),
        "profiles": [("estudante", "Sinh viên", "Học.", "graduation-cap"), ("profissional", "Điều dưỡng", "Lâm sàng.", "user-check"), ("profissional", "Cấp cứu", "Nhanh.", "siren"), ("gestor", "Quản lý", "KPI.", "chart"), ("academico", "Giảng viên", "Tài liệu.", "book"), ("gestor", "Tổ chức", "B2B.", "building")],
        "featured": [("Truyền dịch", "Giọt/p.", "TOOL.INFUSION", "Dùng"), ("Braden", "Loét.", "TOOL.BRADEN", "Áp dụng"), ("BMI", "Chỉ số.", "TOOL.BMI", "Dùng"), ("Dịch", "Cân bằng.", None, "Dùng")],
        "featured_title": "Công cụ phổ biến", "featured_all": "Tất cả",
    },
    "zh-CN": {
        "hero": ("更高效、更可持续的", "护理所需的技术与知识。",
                 "为学生、护士、管理者和医疗机构提供的临床工具、协议、量表和教育内容。",
                 "临床环境中的护士", "探索工具", "了解平台",
                 [("195+", "连接国家"), ("数百", "专业人士"), ("+100", "数字工具")]),
        "search": ("今天需要什么？", "例：滴速、Braden、胰岛素…", "搜索"),
        "seo": ("Nursing Calculators | 全球临床智能平台", "可持续护理技术。195+国家。"),
        "profile": ("个性化体验", "按职业档案定制内容与工具。"),
        "feed": ("临床动态", "实时平台资讯。", "查看全部", "每日提示", "更多"),
        "os": ("Calculadoras de Enfermagem 生态系统", "护理、管理、教育与可持续的连接。", "探索生态",
               [("护理", "计算器与协议。"), ("教育", "文章与模拟。"), ("管理", "指标与质量。"), ("可持续", "Digital first。")]),
        "kh": ("应用知识", "从文章到认证。", "开始", ["文章", "闪卡", "测验", "病例", "证书"]),
        "cases": ("临床培训", "交互式病例。", "全部", ["成人", "儿科", "ICU", "急诊", "手术", "家庭"]),
        "comp": ("我的发展", "能力评估。", ["技术", "科学", "管理", "领导", "患者安全", "可持续"], "初始评估", "我的路径"),
        "ai": ("临床助手", "人工监督的AI。", ["临床问答", "个性化", "学习计划", "协议", "模拟"], "AI不替代临床决策。", "对话"),
        "safety": ("患者安全中心", "IPSG。", "中心", ["IPSG", "不良事件", "险兆", "通知", "协议"]),
        "occ": ("职业健康", "风险管理。", "职业健康"),
        "impact": ("平台影响", "真实使用。", ["计算", "协议", "决策树", "模拟", "学时"]),
        "sust": ("数字可持续", "Digital first。", "可持续", ["纸张", "CO₂", "100%数字"]),
        "gov": ("治理透明", "信任。", "中心", ["LGPD", "Cookies", "AI", "可持续", "无障碍", "方法"], "科学可信", "专家审核。", ["编委会", "专家", "评审"], "伙伴", ["大学", "医院", "学会"]),
        "cta": ("准备好提升护理实践？", "195+国家。", "免费账户", "工具"),
        "profiles": [("estudante", "学生", "学习。", "graduation-cap"), ("profissional", "临床护士", "工具。", "user-check"), ("profissional", "急诊", "快速。", "siren"), ("gestor", "管理者", "KPI。", "chart"), ("academico", "教师", "资源。", "book"), ("gestor", "机构", "B2B。", "building")],
        "featured": [("滴速计算", "滴/分。", "TOOL.INFUSION", "使用"), ("Braden", "压疮。", "TOOL.BRADEN", "应用"), ("BMI", "体重指数。", "TOOL.BMI", "使用"), ("水平衡", "液体。", None, "使用")],
        "featured_title": "最常用工具", "featured_all": "全部",
    },
    "hi-IN": {
        "hero": ("अधिक कुशल और स्थायी", "नर्सिंग के लिए प्रौद्योगिकी और ज्ञान।",
                 "छात्रों, नर्सों, प्रबंधकों और स्वास्थ्य संस्थानों के लिए क्लिनिकल उपकरण।",
                 "Clinical setting में nurse", "उपकरण देखें", "प्लेटफ़ॉर्म",
                 [("195+", "देश"), ("सैकड़ों", "पेशेवर"), ("+100", "डिजिटल उपकरण")]),
        "search": ("आज क्या चाहिए?", "जैसे: Drip, Braden, Insulin…", "खोजें"),
        "seo": ("Nursing Calculators | Global clinical platform", "Sustainable nursing tech."),
        "profile": ("अनुभव personalize करें", "Profile-based content."),
        "feed": ("Clinical updates", "Real-time news.", "सभी", "Tip", "More"),
        "os": ("Ecosystem", "Care-education link.", "Explore",
               [("Care", "Calculators."), ("Education", "Articles."), ("Management", "KPI."), ("Sustainability", "Digital.")]),
        "kh": ("Applied knowledge", "Article to cert.", "Start", ["Article", "Flashcard", "Quiz", "Case", "Cert"]),
        "cases": ("Clinical training", "Cases.", "All", ["Adult", "Peds", "ICU", "ER", "OR", "Family"]),
        "comp": ("Development", "Competencies.", ["Tech", "Sci", "Mgmt", "Lead", "Safety", "Sust"], "Assessment", "Path"),
        "ai": ("Assistant", "Supervised AI.", ["Q&A", "Content", "Plan", "Protocol", "Sim"], "Not clinical decision.", "Chat"),
        "safety": ("Safety center", "IPSG.", "Center", ["IPSG", "Events", "Near miss", "Notify", "Protocol"]),
        "occ": ("Occupational health", "Risk.", "OH"),
        "impact": ("Impact", "Usage.", ["Calc", "Protocol", "Tree", "Sim", "Hours"]),
        "sust": ("Digital sustainability", "Digital first.", "Learn", ["Paper", "CO₂", "100%"]),
        "gov": ("Governance", "Trust.", "Center", ["LGPD", "Cookies", "AI", "Sust", "A11y", "Method"], "Credibility", "Reviewed.", ["Board", "Experts", "Review"], "Partners", ["Univ", "Hosp", "Soc"]),
        "cta": ("Ready?", "195+ countries.", "Free account", "Tools"),
        "profiles": [("estudante", "Student", "Learn.", "graduation-cap"), ("profissional", "Nurse", "Clinical.", "user-check"), ("profissional", "ER", "Fast.", "siren"), ("gestor", "Manager", "KPI.", "chart"), ("academico", "Faculty", "Teach.", "book"), ("gestor", "Inst", "B2B.", "building")],
        "featured": [("Drip calc", "gtt/min.", "TOOL.INFUSION", "Use"), ("Braden", "Ulcer.", "TOOL.BRADEN", "Apply"), ("BMI", "BMI.", "TOOL.BMI", "Use"), ("Fluid", "Balance.", None, "Use")],
        "featured_title": "Popular tools", "featured_all": "All",
    },
    "th-TH": {
        "hero": ("เทคโนโลยีและความรู้เพื่อ", "การพยาบาลที่มีประสิทธิภาพและยั่งยืน",
                 "เครื่องมือทางคลินิก โปรโตคอล สเกล และเนื้อหาการศึกษาสำหรับนักศึกษา พยาบาล ผู้บริหาร และสถ institution",
                 "พยาบาลในสภาพแวดล้อมคลินิก", "สำรวจเครื่องมือ", "เกี่ยวกับแพลตฟอร์ม",
                 [("195+", "ประเทศ"), ("หลายร้อย", "ผู้เชี่ยวชาญ"), ("+100", "เครื่องมือดิจิทัล")]),
        "search": ("วันนี้ต้องการอะไร?", "เช่น Drip, Braden, Insulin…", "ค้นหา"),
        "seo": ("Nursing Calculators | แพลตฟอร์มปัญญาคlinical", "เทคโนโลยีพยาบาลยั่งยืน"),
        "profile": ("ปรับแต่งประสบการณ์", "เนื้อหาตามโปรไฟล์"),
        "feed": ("อัปเดตคlinical", "ข่าวแพลตฟอร์ม", "ทั้งหมด", "เคล็ดลับวันนี้", "เพิ่มเติม"),
        "os": ("Ecosystem", "เชื่อมการดูแล การจัดการ การศึกษา", "สำรวจ",
               [("การดูแล", "เครื่องคิดเลข"), ("การศึกษา", "บทความ"), ("การจัดการ", "ตัวชี้วัด"), ("ความยั่งยืน", "Digital first")]),
        "kh": ("ความรู้ประยุกต์", "บทความสู่ใบรับรอง", "เริ่ม", ["บทความ", "Flashcard", "Quiz", "เคส", "ใบรับรอง"]),
        "cases": ("ฝึกคlinical", "เคสโต้ตอบ", "ทั้งหมด", ["ผู้ใหญ่", "เด็ก", "ICU", "ฉุกเฉิน", "ห้องผ่าตัด", "ครอบครัว"]),
        "comp": ("พัฒนาการ", "สมรรถนะ", ["เทคนิค", "วิทย์", "จัดการ", "ภาวะผู้นำ", "ความปลอดภัย", "ยั่งยืน"], "ประเมิน", "เส้นทาง"),
        "ai": ("ผู้ช่วยคlinical", "AI มีการกำกับ", ["ตอบคำถาม", "เนื้อหา", "แผนเรียน", "โปรโตคอล", "จำลอง"], "AI ไม่แทนที่การตัดสินใจ", "คุย"),
        "safety": ("ศูนย์ความปลอดภัย", "IPSG", "ศูนย์", ["IPSG", "เหตุการณ์", "เกือบพลาด", "แจ้ง", "โปรโตคอล"]),
        "occ": ("อาชีวอนามัย", "ความเสี่ยง", "อาชีวอนามัย"),
        "impact": ("ผลกระทบ", "การใช้งาน", ["คำนวณ", "โปรโตคอล", "ต้นไม้", "จำลอง", "ชั่วโมง"]),
        "sust": ("ความยั่งยืนดิจิทัล", "Digital first", "ยั่งยืน", ["กระดาษ", "CO₂", "100% ดิจิทัล"]),
        "gov": ("ธรรมาภิบาล", "ความไว้วางใจ", "ศูนย์", ["LGPD", "Cookies", "AI", "ยั่งยืน", "การเข้าถึง", "วิธีการ"], "ความน่าเชื่อถือ", "ผู้เชี่ยวชาญ", ["บรรณาธิการ", "ผู้เชี่ยวชาญ", "Review"], "พันธมิตร", ["มหาวิทยาลัย", "โรงพยาบาล", "สมาคม"]),
        "cta": ("พร้อมยกระดับการปฏิบัติ?", "195+ ประเทศ", "บัญชีฟรี", "เครื่องมือ"),
        "profiles": [("estudante", "นักศึกษา", "เรียน", "graduation-cap"), ("profissional", "พยาบาล", "คlinical", "user-check"), ("profissional", "ฉุกเฉิน", "เร็ว", "siren"), ("gestor", "ผู้บริหาร", "KPI", "chart"), ("academico", "อาจารย์", "สอน", "book"), ("gestor", "สถ institution", "B2B", "building")],
        "featured": [("Drip", "หยด/นาที", "TOOL.INFUSION", "ใช้"), ("Braden", "แผลกด", "TOOL.BRADEN", "ใช้"), ("BMI", "BMI", "TOOL.BMI", "ใช้"), ("ของเหลว", "สมดุล", None, "ใช้")],
        "featured_title": "เครื่องมือยอดนิยม", "featured_all": "ทั้งหมด",
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _hero_block(t: tuple) -> dict:
    title, accent, sub, alt, c1, c2, stats = t
    return {
        "title": title, "title_accent": accent, "subtitle": sub,
        "image": "homepage-hero.webp", "image_alt": alt,
        "background": {"color_start": "#002d62", "color_mid": "#0a1628", "color_end": "#334e68"},
        "cta_primary": {"label": c1, "href": "/ferramentas"},
        "cta_secondary": {"label": c2, "href": "/sobre"},
        "stats": [{"value": v, "label": l} for v, l in stats],
    }


def _featured(items: list) -> dict:
    out_items = []
    for title, desc, code, action in items:
        item: dict[str, Any] = {"title": title, "description": desc, "action_label": action}
        if code:
            item["tool_code"] = code
        else:
            item["href"] = "/calculadoras"
        out_items.append(item)
    return {
        "title": items[0][0].split()[0] + "…",  # overwritten below per locale in build
        "view_all_label": "…",
        "view_all_href": "/ferramentas",
        "items": out_items,
    }


def build_locale_doc(locale: str, cfg: dict[str, Any], template: dict) -> dict:
    out = deepcopy(template)
    out["locale"] = locale
    out["generated_at"] = _now_iso()
    out["i18n_status"] = "translated"
    out["partition"] = "locale"
    out["hero"] = _hero_block(cfg["hero"])
    out["search"] = {"label": cfg["search"][0], "placeholder": cfg["search"][1], "button": cfg["search"][2]}
    out["seo"] = {"title": cfg["seo"][0], "description": cfg["seo"][1]}

    feat = _featured(cfg["featured"])
    # fix featured titles per language - use first item context
    feat["title"] = cfg.get("featured_title", "Featured tools")
    feat["view_all_label"] = cfg.get("featured_all", "View all")
    out["featured"] = feat

    p = cfg["profile"]
    prof = cfg["profiles"]
    out["profile_selector"] = {
        "title": p[0], "subtitle": p[1], "default_profile": "profissional",
        "items": [{"code": c, "label": l, "description": d, "href": "/educacao", "icon": i} for c, l, d, i in prof],
    }

    f = cfg["feed"]
    out["clinical_feed"] = {
        "title": f[0], "subtitle": f[1], "view_all_label": f[2], "view_all_href": "/dicas",
        "badge": f[3], "more_label": f[4], "more_href": "/dicas",
        "feed_source": "CMS.DYNAMIC", "max_items_displayed": 6,
        "categories": [{"label": f[3], "icon": "file-text"}],
    }

    o = cfg["os"]
    if len(o) == 4 and isinstance(o[3], list):
        os_title, os_sub, os_cta, orbits = o
    else:
        os_title, os_sub = o[0], o[1]
        orbits = [o[2 + i] for i in range(4)]
        os_cta = o[6]
    positions = ["right", "top", "left", "bottom"]
    icons = ["calculator", "book", "chart", "leaf"]
    hrefs = ["/calculadoras", "/educacao", "/gestao", "/sustentabilidade"]
    out["nursing_os_map"] = {
        "title": os_title, "subtitle": os_sub, "layout": "orbital",
        "center_node": {"label": "Nursing OS", "icon": "network"},
        "orbit_nodes": [
            {"label": orbits[i][0], "description": orbits[i][1], "href": hrefs[i], "icon": icons[i], "position": positions[i]}
            for i in range(4)
        ],
        "cta": {"label": os_cta, "href": "/ferramentas"},
    }

    k = cfg["kh"]
    flow_icons = ["document", "lightbulb", "check-circle", "stethoscope", "award"]
    out["knowledge_hub"] = {
        "title": k[0], "subtitle": k[1],
        "flow": [{"step": i + 1, "label": k[3][i], "icon": flow_icons[i]} for i in range(5)],
        "items": [
            {"title": "Articles", "href": "/artigos", "icon": "document"},
            {"title": "Cases", "href": "/simulados", "icon": "stethoscope"},
            {"title": "Flashcards", "href": "/flashcards", "icon": "lightbulb"},
            {"title": "Simulations", "href": "/simulados", "icon": "play"},
            {"title": "Guides", "href": "/biblioteca", "icon": "file-text"},
            {"title": "Library", "href": "/biblioteca", "icon": "book"},
        ],
        "cta": {"label": k[2], "href": "/educacao"},
        "image": "homepage-section-001.webp", "image_alt": k[0],
    }

    c = cfg["cases"]
    case_icons = ["user", "baby", "activity", "siren", "scissors", "home"]
    out["clinical_cases"] = {
        "title": c[0], "subtitle": c[1], "view_all_label": c[2], "view_all_href": "/simulados",
        "items": [{"title": c[3][i], "href": "/simulados", "icon": case_icons[i]} for i in range(6)],
    }

    cp = cfg["comp"]
    track_icons = ["tool", "flask", "chart", "users", "shield", "leaf"]
    out["competency_track"] = {
        "title": cp[0], "subtitle": cp[1],
        "tracks": [{"label": cp[2][i], "icon": track_icons[i]} for i in range(6)],
        "initial_assessment": {"label": cp[3], "href": "/trilhas"},
        "cta": {"label": cp[4], "href": "/trilhas"},
    }

    a = cfg["ai"]
    cap_icons = ["message-circle", "sparkles", "calendar", "file-text", "play"]
    out["ai_assistant"] = {
        "title": a[0], "subtitle": a[1],
        "capabilities": [{"label": a[2][i], "icon": cap_icons[i]} for i in range(5)],
        "disclaimer": a[3], "cta": {"label": a[4], "href": "/ferramentas"},
    }

    s = cfg["safety"]
    s_icons = ["target", "alert-triangle", "eye", "bell", "clipboard"]
    out["patient_safety_center"] = {
        "title": s[0], "subtitle": s[1],
        "items": [{"title": s[3][i], "href": "/gestao", "icon": s_icons[i]} for i in range(5)],
        "cta": {"label": s[2], "href": "/gestao"},
    }

    oc = cfg["occ"]
    out["occupational_health"] = {
        "title": oc[0], "subtitle": oc[1],
        "items": [
            {"title": "PGR", "description": "Risk program.", "href": "/gestao", "icon": "clipboard"},
            {"title": "GRO", "description": "Occupational risk.", "href": "/gestao", "icon": "shield"},
            {"title": "Biological", "description": "Exposure control.", "href": "/gestao", "icon": "biohazard"},
            {"title": "NR-01", "description": "SST management.", "href": "/gestao", "icon": "hardhat"},
            {"title": "NR-32", "description": "Healthcare safety.", "href": "/gestao", "icon": "hardhat"},
            {"title": "Mental health", "description": "Prevention support.", "href": "/gestao", "icon": "heart"},
            {"title": "Ergonomics", "description": "Safe practice.", "href": "/gestao", "icon": "activity"},
        ],
        "cta": {"label": oc[2], "href": "/gestao"},
    }

    im = cfg["impact"]
    bindings = ["total_calculations", "protocols_accessed", "decision_trees_used", "simulations_completed", "study_hours_logged"]
    icons = ["calculator", "clipboard", "git-branch", "play", "clock"]
    vals = ["2,4M", "890K", "156K", "420K", "1,1M"]
    out["impact_dashboard"] = {
        "title": im[0], "subtitle": im[1], "data_source": "ANALYTICS.AGGREGATED", "refresh_interval": "daily",
        "metrics": [{"binding": bindings[i], "label": im[2][i], "icon": icons[i], "suffix": "+", "value": vals[i]} for i in range(5)],
    }

    su = cfg["sust"]
    out["sustainability_block"] = {
        "title": su[0], "subtitle": su[1], "data_source": "ANALYTICS.AGGREGATED",
        "metrics": [
            {"binding": "paper_sheets_saved", "label": su[3][0], "icon": "leaf", "suffix": "+", "value": "3,2M"},
            {"binding": "co2_reduced_kg", "label": su[3][1], "icon": "wind", "suffix": "+", "value": "48K"},
            {"binding": "digital_protocols_pct", "label": su[3][2], "icon": "document", "suffix": "%", "value": "94"},
        ],
        "cta": {"label": su[2], "href": "/sustentabilidade"},
    }

    g = cfg["gov"]
    gov_icons = ["shield", "cookie", "brain", "leaf", "users", "flask"]
    gov_hrefs = ["/privacidade"] * 2 + ["/sustentabilidade"] * 2 + ["/acessibilidade", "/sobre"]
    out["governance_center"] = {
        "title": g[0], "subtitle": g[1],
        "items": [{"title": g[3][i], "href": gov_hrefs[i], "icon": gov_icons[i]} for i in range(6)],
        "scientific_credibility": {
            "title": g[4], "subtitle": g[5],
            "items": [{"title": g[6][i], "href": "/sobre", "icon": "users"} for i in range(3)],
            "partners": {"title": g[7], "categories": list(g[8])},
        },
        "cta": {"label": g[2], "href": "/privacidade"},
    }

    ct = cfg["cta"]
    out["cta_final"] = {
        "title": ct[0], "subtitle": ct[1],
        "cta_primary": {"label": ct[2], "href": "/login"},
        "cta_secondary": {"label": ct[3], "href": "/ferramentas"},
    }

    out.pop("daily_tip", None)
    out.pop("education_block", None)
    return out


def main() -> int:
    if not TEMPLATE.is_file():
        print("Missing template", file=sys.stderr)
        return 1
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    # featured title overrides
    LOCALE_META = {
        "cs-CZ": {"featured_title": "Nejpoužívanější nástroje", "featured_all": "Zobrazit všechny nástroje"},
        "pl-PL": {"featured_title": "Najczęściej używane narzędzia", "featured_all": "Zobacz wszystkie"},
        "nl-NL": {"featured_title": "Meest gebruikte tools", "featured_all": "Alle tools"},
        "ar": {"featured_title": "الأدوات الأكثر استخداماً", "featured_all": "عرض الكل"},
        "ru-RU": {"featured_title": "Популярные инструменты", "featured_all": "Все"},
        "ko-KR": {"featured_title": "가장 많이 쓰는 도구", "featured_all": "전체"},
        "tr-TR": {"featured_title": "En çok kullanılan", "featured_all": "Tümü"},
        "id-ID": {"featured_title": "Alat paling populer", "featured_all": "Semua"},
        "vi-VN": {"featured_title": "Công cụ phổ biến", "featured_all": "Tất cả"},
        "zh-CN": {"featured_title": "最常用工具", "featured_all": "全部"},
        "hi-IN": {"featured_title": "Popular tools", "featured_all": "All"},
        "th-TH": {"featured_title": "เครื่องมือยอดนิยม", "featured_all": "ทั้งหมด"},
    }

    for locale, cfg in LOCALES.items():
        cfg = {**cfg, **LOCALE_META.get(locale, {})}
        doc = build_locale_doc(locale, cfg, template)
        dst = BY_LOCALE / locale / "home_page.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(dst.relative_to(ROOT))

    print(f"Wrote {len(LOCALES)} locale(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
