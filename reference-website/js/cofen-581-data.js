/**
 * COFEN 581/2018 — Especialidades de Enfermagem
 * Estruturado por área de abrangência para alimentar trilhas de conhecimento
 * Atualizado com Decisões 065/2021, 120/2021, 263/2023, 264/2023, 21/2024
 */

window.COFEN_581_2018 = {
  "lei": "Resolução COFEN nº 581/2018",
  "alteracoes": [
    "Resolução COFEN nº 625/2020",
    "Resolução COFEN nº 610/2019",
    "Decisão COFEN nº 065/2021 — Enfermagem Nuclear",
    "Decisão COFEN nº 120/2021 — Bases Epistemológicas e Filosóficas",
    "Decisão COFEN nº 263/2023 — Podiatria Clínica",
    "Decisão COFEN nº 264/2023 — Reabilitação",
    "Decisão COFEN nº 21/2024 — História da Enfermagem"
  ],
  "areas": {
    "I": {
      "titulo": "Saúde Coletiva; Saúde da Criança e do Adolescente; Saúde do Adulto; Saúde do Idoso; Urgência e Emergência",
      "cor": "var(--blue-600)",
      "especialidades": [
        { "id": "enf-aeroespacial", "nome": "Enfermagem Aeroespacial", "categoria": "Urgência e Emergência" },
        { "id": "enf-aquaviaria", "nome": "Enfermagem Aquaviária", "categoria": "Urgência e Emergência" },
        { "id": "enf-acesso-vascular", "nome": "Enfermagem em Acesso Vascular e Terapia Infusional", "categoria": "Saúde do Adulto" },
        { "id": "enf-anestesiologia", "nome": "Assistência de Enfermagem em Anestesiologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-assistencia-domiciliar", "nome": "Enfermagem em Assistência Domiciliária", "categoria": "Saúde do Adulto" },
        { "id": "enf-saude-coletiva", "nome": "Enfermagem em Saúde Coletiva", "categoria": "Saúde Coletiva", "subespecialidades": ["Saúde da Família e Comunidade", "Saúde Pública", "Saúde Ambiental"] },
        { "id": "enf-capatacao-transplante", "nome": "Enfermagem em Captação, Doação e Transplante de Órgãos e Tecidos", "categoria": "Saúde do Adulto" },
        { "id": "enf-cardiologia", "nome": "Enfermagem em Cardiologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-central-esterilizacao", "nome": "Enfermagem em Central de Material e Esterilização (CME)", "categoria": "Saúde do Adulto" },
        { "id": "enf-cirurgia", "nome": "Enfermagem Cirúrgica / Centro Cirúrgico", "categoria": "Saúde do Adulto" },
        { "id": "enf-cuidados-paliativos", "nome": "Enfermagem em Cuidados Paliativos", "categoria": "Saúde do Adulto" },
        { "id": "enf-dermatologia", "nome": "Enfermagem em Dermatologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-diabetes", "nome": "Enfermagem em Diabetes", "categoria": "Saúde do Adulto" },
        { "id": "enf-dialise", "nome": "Enfermagem em Diálise e Nefrologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-doencas-infecciosas", "nome": "Enfermagem em Doenças Infecciosas e Parasitárias", "categoria": "Saúde Coletiva" },
        { "id": "enf-endoscopia", "nome": "Enfermagem em Endoscopia", "categoria": "Saúde do Adulto" },
        { "id": "enf-estomaterapia", "nome": "Enfermagem em Estomaterapia", "categoria": "Saúde do Adulto" },
        { "id": "enf-gastroenterologia", "nome": "Enfermagem em Gastroenterologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-hemoterapia", "nome": "Enfermagem em Hemoterapia e Hematologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-imunizacao", "nome": "Enfermagem em Imunização", "categoria": "Saúde Coletiva" },
        { "id": "enf-mastologia", "nome": "Enfermagem em Mastologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-medicina-interna", "nome": "Enfermagem em Medicina Interna", "categoria": "Saúde do Adulto" },
        { "id": "enf-nefrologia", "nome": "Enfermagem em Nefrologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-neurologia", "nome": "Enfermagem em Neurologia e Neurocirurgia", "categoria": "Saúde do Adulto" },
        { "id": "enf-obstetricia", "nome": "Enfermagem em Obstetrícia", "categoria": "Saúde da Mulher" },
        { "id": "enf-oncologia", "nome": "Enfermagem em Oncologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-ortopedia", "nome": "Enfermagem em Ortopedia e Traumatologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-pediatria", "nome": "Enfermagem em Pediatria", "categoria": "Saúde da Criança e do Adolescente" },
        { "id": "enf-pneumologia", "nome": "Enfermagem em Pneumologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-podiatria", "nome": "Podiatria Clínica", "categoria": "Saúde do Adulto", "decisao": "263/2023" },
        { "id": "enf-psiquiatria", "nome": "Enfermagem em Saúde Mental e Psiquiatria", "categoria": "Saúde do Adulto" },
        { "id": "enf-reabilitacao", "nome": "Enfermagem em Reabilitação", "categoria": "Saúde do Adulto", "decisao": "264/2023" },
        { "id": "enf-recuperacao", "nome": "Enfermagem em Recuperação Anestésica (RA)", "categoria": "Saúde do Adulto" },
        { "id": "enf-roi", "nome": "Enfermagem em Reparação de Lesões e Inflamações Cutâneas", "categoria": "Saúde do Adulto" },
        { "id": "enf-saude-adulto", "nome": "Enfermagem em Saúde do Adulto", "categoria": "Saúde do Adulto" },
        { "id": "enf-saude-crianca", "nome": "Enfermagem em Saúde da Criança e do Adolescente", "categoria": "Saúde da Criança e do Adolescente" },
        { "id": "enf-saude-idoso", "nome": "Enfermagem em Saúde do Idoso / Gerontologia", "categoria": "Saúde do Idoso" },
        { "id": "enf-saude-mulher", "nome": "Enfermagem em Saúde da Mulher", "categoria": "Saúde da Mulher" },
        { "id": "enf-terapia-intensiva", "nome": "Enfermagem em Terapia Intensiva", "categoria": "Urgência e Emergência" },
        { "id": "enf-trauma", "nome": "Enfermagem em Trauma e Emergência", "categoria": "Urgência e Emergência" },
        { "id": "enf-urologia", "nome": "Enfermagem em Urologia", "categoria": "Saúde do Adulto" },
        { "id": "enf-nuclear", "nome": "Enfermagem Nuclear", "categoria": "Saúde do Adulto", "decisao": "065/2021" }
      ]
    },
    "II": {
      "titulo": "Gestão",
      "cor": "var(--blue-700)",
      "especialidades": [
        { "id": "enf-auditoria", "nome": "Enfermagem em Auditoria", "categoria": "Gestão" },
        { "id": "enf-direito-sanitario", "nome": "Direito Sanitário", "categoria": "Gestão" },
        { "id": "enf-economia-saude", "nome": "Economia da Saúde", "categoria": "Gestão" },
        { "id": "enf-gerenciamento", "nome": "Enfermagem em Gerenciamento/Gestão", "categoria": "Gestão", "subespecialidades": ["Administração Hospitalar", "Gestão de Saúde", "Gestão de Enfermagem"] },
        { "id": "enf-qualidade", "nome": "Enfermagem em Qualidade e Segurança do Paciente", "categoria": "Gestão" },
        { "id": "enf-projetos", "nome": "Enfermagem em Projetos e Processos", "categoria": "Gestão" }
      ]
    },
    "III": {
      "titulo": "Ensino e Pesquisa",
      "cor": "var(--navy-900)",
      "especialidades": [
        { "id": "enf-bioetica", "nome": "Bioética", "categoria": "Ensino e Pesquisa" },
        { "id": "enf-educacao", "nome": "Educação em Enfermagem", "categoria": "Ensino e Pesquisa" },
        { "id": "enf-metodologia-ensino", "nome": "Metodologia do Ensino Superior", "categoria": "Ensino e Pesquisa" },
        { "id": "enf-metodologia-pesquisa", "nome": "Metodologia da Pesquisa Científica", "categoria": "Ensino e Pesquisa" },
        { "id": "enf-docencia", "nome": "Docência do Ensino Superior", "categoria": "Ensino e Pesquisa" },
        { "id": "enf-bases-epistemologicas", "nome": "Bases Epistemológicas e Filosóficas da Enfermagem", "categoria": "Ensino e Pesquisa", "decisao": "120/2021" },
        { "id": "enf-historia", "nome": "História da Enfermagem", "categoria": "Ensino e Pesquisa", "decisao": "21/2024" }
      ]
    }
  },

  // Trilhas de conhecimento geradas a partir das especialidades
  // Cada trilha vincula especialidade → calculadoras + recursos do site
  "trilhas": {
    "enf-terapia-intensiva": {
      "calculadoras": ["apache.html", "sofa.html", "saps.html", "news2.html", "mews.html", "glasgow.html", "sass.html", "ramsay.html", "richmond.html", "rass.html"],
      "recursos": ["simulados.html", "flashcards.html", "caso-clinico.html", "protocolos.html", "sbar.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00047", "NANDA_00049", "NANDA_00200"],
      "desc": "UTI, monitorização, suporte ventilatório e estabilização hemodinâmica"
    },
    "enf-trauma": {
      "calculadoras": ["news2.html", "mews.html", "glasgow.html", "rts.html", "fast.html", "curb65.html", "qsofa.html"],
      "recursos": ["simulados.html", "sbar.html", "protocolos.html", "caso-clinico.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132", "NANDA_00200"],
      "desc": "Atendimento pré-hospitalar, sala de emergência e trauma"
    },
    "enf-pediatria": {
      "calculadoras": ["apgar.html", "ballard.html", "capurro.html", "flacc.html", "wong-baker.html", "pews.html", "glasgow-pediatrico.html", "silverman-andersen.html"],
      "recursos": ["simulados.html", "flashcards.html", "caso-clinico.html", "biblioteca.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132", "NANDA_00234"],
      "desc": "Cuidados neonatais, pediátricos e do adolescente"
    },
    "enf-obstetricia": {
      "calculadoras": ["apgar.html", "ballard.html", "bishop.html", "gestacional.html", "capurro.html", "imc-gestacional.html"],
      "recursos": ["simulados.html", "flashcards.html", "caso-clinico.html", "protocolos.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00200", "NANDA_00234"],
      "desc": "Pré-natal, parto, puerpério e saúde reprodutiva"
    },
    "enf-cardiologia": {
      "calculadoras": ["news2.html", "mews.html", "cha2ds2vasc.html", "hasbled.html", "heart-score.html", "curb65.html", "sofa.html"],
      "recursos": ["simulados.html", "flashcards.html", "caso-clinico.html", "protocolos.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00047", "NANDA_00200"],
      "desc": "Monitorização cardiovascular, arritmias e ICC"
    },
    "enf-oncologia": {
      "calculadoras": ["ecog.html", "glasgow.html", "phq9.html", "zarit.html", "barthel.html", "nrs2002.html"],
      "recursos": ["simulados.html", "flashcards.html", "caso-clinico.html", "biblioteca.html", "sala-descompressao.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132", "NANDA_00200", "NANDA_00234"],
      "desc": "Quimioterapia, radioterapia, cuidados paliativos oncológicos"
    },
    "enf-saude-idoso": {
      "calculadoras": ["barthel.html", "lawton.html", "mini-cog.html", "zarit.html", "gds.html", "braden.html", "norton.html", "waterlow.html", "tug.html", "morse.html"],
      "recursos": ["simulados.html", "flashcards.html", "caso-clinico.html", "biblioteca.html", "sala-descompressao.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132", "NANDA_00200", "NANDA_00234"],
      "desc": "Geriatria, fragilidade, polifarmácia e qualidade de vida"
    },
    "enf-saude-mental": {
      "calculadoras": ["phq9.html", "gds.html", "hamilton.html", "ciwa-ar.html", "cornell.html", "zarit.html"],
      "recursos": ["simulados.html", "flashcards.html", "caso-clinico.html", "sala-descompressao.html", "biblioteca.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132", "NANDA_00200"],
      "desc": "Saúde mental, transtornos psiquiátricos e abuso de substâncias"
    },
    "enf-cirurgia": {
      "calculadoras": ["asa.html", "aldrete.html", "checklist-cirurgico-seguro.html", "ecog.html"],
      "recursos": ["simulados.html", "flashcards.html", "protocolos.html", "caso-clinico.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132", "NANDA_00200"],
      "desc": "Centro cirúrgico, recuperação anestésica e perioperatório"
    },
    "enf-saude-coletiva": {
      "calculadoras": ["abcd2.html", "centor.html", "curb65.html", "news2.html"],
      "recursos": ["simulados.html", "flashcards.html", "biblioteca.html", "legislacoes.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132", "NANDA_00200"],
      "desc": "Saúde da família, vigilância e atenção primária"
    },
    "enf-diabetes": {
      "calculadoras": ["insulina.html", "gotejamento.html", "parkland.html", "news2.html"],
      "recursos": ["simulados.html", "flashcards.html", "medicamentos.html", "regrasmedicacoes.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132", "NANDA_00200"],
      "desc": "Educação em diabetes, insulinoterapia e complicações"
    },
    "enf-estomaterapia": {
      "calculadoras": ["braden.html", "norton.html", "waterlow.html", "push.html"],
      "recursos": ["simulados.html", "flashcards.html", "protocolos.html", "caso-clinico.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132", "NANDA_00200"],
      "desc": "Feridas, ostomias, incontinências e lesões cutâneas"
    },
    "enf-gerenciamento": {
      "calculadoras": ["dimensionamento.html", "calculohoraextra.html", "adicionalnoturno.html", "calcularferias.html", "copsoq.html", "copsoq3.html"],
      "recursos": ["simulados.html", "biblioteca.html", "legislacoes.html", "normas-regulamentadoras.html"],
      "diagnosticos": [],
      "desc": "Gestão de pessoas, dimensionamento, qualidade e processos"
    },
    "enf-auditoria": {
      "calculadoras": ["dimensionamento.html", "copsoq.html"],
      "recursos": ["legislacoes.html", "biblioteca.html", "protocolos.html"],
      "diagnosticos": [],
      "desc": "Auditoria assistencial, contábil e operacional em saúde"
    },
    "enf-cuidados-paliativos": {
      "calculadoras": ["ecog.html", "barthel.html", "lawton.html", "phq9.html", "zarit.html", "escalanumerica.html", "wong-baker.html"],
      "recursos": ["simulados.html", "caso-clinico.html", "sala-descompressao.html", "biblioteca.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132", "NANDA_00200"],
      "desc": "Cuidados ao fim da vida, controle de sintomas e suporte familiar"
    },
    "enf-neurologia": {
      "calculadoras": ["glasgow.html", "nihss.html", "four.html", "abcd2.html", "glasgow-pupilas.html", "escalanumerica.html"],
      "recursos": ["simulados.html", "flashcards.html", "caso-clinico.html", "protocolos.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132", "NANDA_00200"],
      "desc": "AVC, neurocirurgia, monitorização e reabilitação neurológica"
    },
    "enf-nefrologia": {
      "calculadoras": ["sofa.html", "apache.html", "balancohidrico.html", "gotejamento.html"],
      "recursos": ["simulados.html", "flashcards.html", "medicamentos.html", "protocolos.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00200"],
      "desc": "Diálise, transplante renal e nefropatias"
    },
    "enf-dermatologia": {
      "calculadoras": ["braden.html", "norton.html", "waterlow.html"],
      "recursos": ["simulados.html", "flashcards.html", "protocolos.html"],
      "diagnosticos": ["NANDA_00046", "NANDA_00132"],
      "desc": "Dermatologia clínica, feridas e integridade cutânea"
    },
    "enf-docencia": {
      "calculadoras": [],
      "recursos": ["biblioteca.html", "flashcards.html", "simulados.html", "trilha-conhecimento.html", "testes-autoconhecimento.html"],
      "diagnosticos": [],
      "desc": "Metodologias ativas, avaliação e planejamento educacional"
    }
  }
};
