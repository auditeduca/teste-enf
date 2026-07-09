/* ════════════════════════════════════════════════════════════════════
   CARREIRAS DATA — Nursing Career Intelligence
   Top 100 institutions, skills by role, learning paths, sample data
   ════════════════════════════════════════════════════════════════════ */
window.CAREER_DATA = {

  // ═════════════════════════════════════════════════════════════════
  // TOP 100 NURSING INSTITUTIONS (QS + CAPES)
  // ═════════════════════════════════════════════════════════════════
  institutions: [
    // Top 20 Global
    { id:'inst-001', name:'University of Pennsylvania', country:'EUA', region:'Americas', rank:1, programs:['BSN','MSN','DNP','PhD'], site:'upenn.edu' },
    { id:'inst-002', name:'Johns Hopkins University', country:'EUA', region:'Americas', rank:2, programs:['BSN','MSN','DNP','PhD'], site:'jhu.edu' },
    { id:'inst-003', name:'University of Toronto', country:'Canadá', region:'Americas', rank:3, programs:['BScN','MN','PhD'], site:'utoronto.ca' },
    { id:'inst-004', name:"King's College London", country:'Reino Unido', region:'Europa', rank:4, programs:['BSc','MSc','PhD'], site:'kcl.ac.uk' },
    { id:'inst-005', name:'University of Edinburgh', country:'Reino Unido', region:'Europa', rank:5, programs:['BN','MSc','PhD'], site:'ed.ac.uk' },
    { id:'inst-006', name:'University of Melbourne', country:'Austrália', region:'Oceania', rank:6, programs:['BN','MN','PhD'], site:'unimelb.edu.au' },
    { id:'inst-007', name:'University of Sydney', country:'Austrália', region:'Oceania', rank:7, programs:['BN','MSc','PhD'], site:'sydney.edu.au' },
    { id:'inst-008', name:'National University of Singapore', country:'Singapura', region:'Ásia', rank:8, programs:['BN','MN','PhD'], site:'nus.edu.sg' },
    { id:'inst-009', name:'University of Alberta', country:'Canadá', region:'Americas', rank:9, programs:['BN','MN','PhD'], site:'ualberta.ca' },
    { id:'inst-010', name:'University of British Columbia', country:'Canadá', region:'Americas', rank:10, programs:['BN','MN','PhD'], site:'ubc.ca' },
    { id:'inst-011', name:'Yale University', country:'EUA', region:'Americas', rank:11, programs:['MSN','DNP','PhD'], site:'yale.edu' },
    { id:'inst-012', name:'University of Michigan', country:'EUA', region:'Americas', rank:12, programs:['BSN','MSN','PhD'], site:'umich.edu' },
    { id:'inst-013', name:'University of Washington', country:'EUA', region:'Americas', rank:13, programs:['BSN','MSN','DNP'], site:'uw.edu' },
    { id:'inst-014', name:'Columbia University', country:'EUA', region:'Americas', rank:14, programs:['MSN','DNP','PhD'], site:'columbia.edu' },
    { id:'inst-015', name:'Duke University', country:'EUA', region:'Americas', rank:15, programs:['BSN','MSN','DNP'], site:'duke.edu' },
    { id:'inst-016', name:'University of Pittsburgh', country:'EUA', region:'Americas', rank:16, programs:['BSN','MSN','PhD'], site:'pitt.edu' },
    { id:'inst-017', name:'University of Southampton', country:'Reino Unido', region:'Europa', rank:17, programs:['BSc','MSc','PhD'], site:'southampton.ac.uk' },
    { id:'inst-018', name:'University of Manchester', country:'Reino Unido', region:'Europa', rank:18, programs:['BN','MSc','PhD'], site:'manchester.ac.uk' },
    { id:'inst-019', name:'University of Glasgow', country:'Reino Unido', region:'Europa', rank:19, programs:['BN','MSc','PhD'], site:'gla.ac.uk' },
    { id:'inst-020', name:'University of Technology Sydney', country:'Austrália', region:'Oceania', rank:20, programs:['BN','MN','PhD'], site:'uts.edu.au' },
    // 21-40
    { id:'inst-021', name:'University of California–San Francisco', country:'EUA', region:'Americas', rank:21, programs:['MSN','DNP','PhD'], site:'ucsf.edu' },
    { id:'inst-022', name:'New York University', country:'EUA', region:'Americas', rank:22, programs:['BSN','MSN','DNP'], site:'nyu.edu' },
    { id:'inst-023', name:'Rush University', country:'EUA', region:'Americas', rank:23, programs:['BSN','MSN','DNP'], site:'rushu.rush.edu' },
    { id:'inst-024', name:'University of North Carolina', country:'EUA', region:'Americas', rank:24, programs:['BSN','MSN','PhD'], site:'unc.edu' },
    { id:'inst-025', name:'Emory University', country:'EUA', region:'Americas', rank:25, programs:['BSN','MSN','DNP'], site:'emory.edu' },
    { id:'inst-026', name:'Case Western Reserve University', country:'EUA', region:'Americas', rank:26, programs:['BSN','MSN','PhD'], site:'case.edu' },
    { id:'inst-027', name:'Ohio State University', country:'EUA', region:'Americas', rank:27, programs:['BSN','MSN','PhD'], site:'osu.edu' },
    { id:'inst-028', name:'University of Illinois Chicago', country:'EUA', region:'Americas', rank:28, programs:['BSN','MSN','PhD'], site:'uic.edu' },
    { id:'inst-029', name:'University of Iowa', country:'EUA', region:'Americas', rank:29, programs:['BSN','MSN','PhD'], site:'uiowa.edu' },
    { id:'inst-030', name:'University of Wisconsin–Madison', country:'EUA', region:'Americas', rank:30, programs:['BSN','MSN','PhD'], site:'wisc.edu' },
    { id:'inst-031', name:'McGill University', country:'Canadá', region:'Americas', rank:31, programs:['BN','MN','PhD'], site:'mcgill.ca' },
    { id:'inst-032', name:'University of Montreal', country:'Canadá', region:'Americas', rank:32, programs:['BSc','MSc','PhD'], site:'umontreal.ca' },
    { id:'inst-033', name:'University of Calgary', country:'Canadá', region:'Americas', rank:33, programs:['BN','MN','PhD'], site:'ucalgary.ca' },
    { id:'inst-034', name:'McMaster University', country:'Canadá', region:'Americas', rank:34, programs:['BScN','MN','PhD'], site:'mcmaster.ca' },
    { id:'inst-035', name:'Karolinska Institutet', country:'Suécia', region:'Europa', rank:35, programs:['BSc','MSc','PhD'], site:'ki.se' },
    { id:'inst-036', name:'University of Amsterdam', country:'Holanda', region:'Europa', rank:36, programs:['BSc','MSc','PhD'], site:'uva.nl' },
    { id:'inst-037', name:'Trinity College Dublin', country:'Irlanda', region:'Europa', rank:37, programs:['BSc','MSc','PhD'], site:'tcd.ie' },
    { id:'inst-038', name:'University of Helsinki', country:'Finlândia', region:'Europa', rank:38, programs:['BN','MSc','PhD'], site:'helsinki.fi' },
    { id:'inst-039', name:'Hong Kong Polytechnic University', country:'Hong Kong', region:'Ásia', rank:39, programs:['BN','MSc','PhD'], site:'polyu.edu.hk' },
    { id:'inst-040', name:'Seoul National University', country:'Coreia do Sul', region:'Ásia', rank:40, programs:['BN','MN','PhD'], site:'snu.ac.kr' },
    // 41-60
    { id:'inst-041', name:'University of Pennsylvania–Pittsburgh', country:'EUA', region:'Americas', rank:41, programs:['BSN','MSN'], site:'pitt.edu' },
    { id:'inst-042', name:'Boston College', country:'EUA', region:'Americas', rank:42, programs:['BSN','MSN','PhD'], site:'bc.edu' },
    { id:'inst-043', name:'Vanderbilt University', country:'EUA', region:'Americas', rank:43, programs:['MSN','DNP','PhD'], site:'vanderbilt.edu' },
    { id:'inst-044', name:'University of Maryland', country:'EUA', region:'Americas', rank:44, programs:['BSN','MSN','PhD'], site:'umaryland.edu' },
    { id:'inst-045', name:'Indiana University', country:'EUA', region:'Americas', rank:45, programs:['BSN','MSN','PhD'], site:'iu.edu' },
    { id:'inst-046', name:'University of Arizona', country:'EUA', region:'Americas', rank:46, programs:['BSN','MSN','DNP'], site:'arizona.edu' },
    { id:'inst-047', name:'University of Florida', country:'EUA', region:'Americas', rank:47, programs:['BSN','MSN','DNP'], site:'ufl.edu' },
    { id:'inst-048', name:'University of Virginia', country:'EUA', region:'Americas', rank:48, programs:['BSN','MSN','PhD'], site:'virginia.edu' },
    { id:'inst-049', name:'University of Colorado', country:'EUA', region:'Americas', rank:49, programs:['BSN','MSN','DNP'], site:'cuanschutz.edu' },
    { id:'inst-050', name:'University of Texas at Austin', country:'EUA', region:'Americas', rank:50, programs:['BSN','MSN','PhD'], site:'utexas.edu' },
    { id:'inst-051', name:'Queen Margaret University', country:'Reino Unido', region:'Europa', rank:51, programs:['BSc','MSc'], site:'qmu.ac.uk' },
    { id:'inst-052', name:'City University London', country:'Reino Unido', region:'Europa', rank:52, programs:['BSc','MSc','PhD'], site:'city.ac.uk' },
    { id:'inst-053', name:'University of Leeds', country:'Reino Unido', region:'Europa', rank:53, programs:['BN','MSc','PhD'], site:'leeds.ac.uk' },
    { id:'inst-054', name:'University of Nottingham', country:'Reino Unido', region:'Europa', rank:54, programs:['BN','MSc','PhD'], site:'nottingham.ac.uk' },
    { id:'inst-055', name:'Cardiff University', country:'Reino Unido', region:'Europa', rank:55, programs:['BN','MSc','PhD'], site:'cardiff.ac.uk' },
    { id:'inst-056', name:'University of Sheffield', country:'Reino Unido', region:'Europa', rank:56, programs:['BN','MSc'], site:'sheffield.ac.uk' },
    { id:'inst-057', name:'University of Adelaide', country:'Austrália', region:'Oceania', rank:57, programs:['BN','MN','PhD'], site:'adelaide.edu.au' },
    { id:'inst-058', name:'Monash University', country:'Austrália', region:'Oceania', rank:58, programs:['BN','MSc','PhD'], site:'monash.edu' },
    { id:'inst-059', name:'Griffith University', country:'Austrália', region:'Oceania', rank:59, programs:['BN','MSc'], site:'griffith.edu.au' },
    { id:'inst-060', name:'Deakin University', country:'Austrália', region:'Oceania', rank:60, programs:['BN','MSc','PhD'], site:'deakin.edu.au' },
    // 61-80
    { id:'inst-061', name:'University of Tokyo', country:'Japão', region:'Ásia', rank:61, programs:['BN','MN','PhD'], site:'u-tokyo.ac.jp' },
    { id:'inst-062', name:'Kyoto University', country:'Japão', region:'Ásia', rank:62, programs:['BN','MN','PhD'], site:'kyoto-u.ac.jp' },
    { id:'inst-063', name:'National Taiwan University', country:'Taiwan', region:'Ásia', rank:63, programs:['BN','MN','PhD'], site:'ntu.edu.tw' },
    { id:'inst-064', name:'Chinese University of Hong Kong', country:'Hong Kong', region:'Ásia', rank:64, programs:['BN','MSc','PhD'], site:'cuhk.edu.hk' },
    { id:'inst-065', name:'University of Auckland', country:'Nova Zelândia', region:'Oceania', rank:65, programs:['BN','MN','PhD'], site:'auckland.ac.nz' },
    { id:'inst-066', name:'Aarhus University', country:'Dinamarca', region:'Europa', rank:66, programs:['BSc','MSc','PhD'], site:'au.dk' },
    { id:'inst-067', name:'University of Oslo', country:'Noruega', region:'Europa', rank:67, programs:['BSc','MSc','PhD'], site:'uio.no' },
    { id:'inst-068', name:'University of Gothenburg', country:'Suécia', region:'Europa', rank:68, programs:['BSc','MSc','PhD'], site:'gu.se' },
    { id:'inst-069', name:'Uppsala University', country:'Suécia', region:'Europa', rank:69, programs:['BSc','MSc','PhD'], site:'uu.se' },
    { id:'inst-070', name:'University of Barcelona', country:'Espanha', region:'Europa', rank:70, programs:['BSc','MSc','PhD'], site:'ub.edu' },
    // Brazil (CAPES)
    { id:'inst-071', name:'USP — Universidade de São Paulo', country:'Brasil', region:'Americas', rank:71, programs:['Bach','MSc','PhD'], site:'usp.br' },
    { id:'inst-072', name:'UNIFESP — Univ. Federal de São Paulo', country:'Brasil', region:'Americas', rank:72, programs:['Bach','MSc','PhD'], site:'unifesp.br' },
    { id:'inst-073', name:'EERP-USP — Esc. Enf. Ribeirão Preto', country:'Brasil', region:'Americas', rank:73, programs:['Bach','MSc','PhD'], site:'eerp.usp.br' },
    { id:'inst-074', name:'UERJ — Univ. Estado Rio de Janeiro', country:'Brasil', region:'Americas', rank:74, programs:['Bach','MSc','PhD'], site:'uerj.br' },
    { id:'inst-075', name:'UFMG — Univ. Federal Minas Gerais', country:'Brasil', region:'Americas', rank:75, programs:['Bach','MSc','PhD'], site:'ufmg.br' },
    { id:'inst-076', name:'UNICAMP — Univ. Estadual Campinas', country:'Brasil', region:'Americas', rank:76, programs:['Bach','MSc','PhD'], site:'unicamp.br' },
    { id:'inst-077', name:'UFSC — Univ. Federal Santa Catarina', country:'Brasil', region:'Americas', rank:77, programs:['Bach','MSc','PhD'], site:'ufsc.br' },
    { id:'inst-078', name:'UFRGS — Univ. Fed. Rio Grande do Sul', country:'Brasil', region:'Americas', rank:78, programs:['Bach','MSc','PhD'], site:'ufrgs.br' },
    { id:'inst-079', name:'UFRJ — Univ. Federal Rio de Janeiro', country:'Brasil', region:'Americas', rank:79, programs:['Bach','MSc','PhD'], site:'ufrj.br' },
    { id:'inst-080', name:'UFPE — Univ. Federal Pernambuco', country:'Brasil', region:'Americas', rank:80, programs:['Bach','MSc','PhD'], site:'ufpe.br' },
    { id:'inst-081', name:'UFC — Univ. Federal Ceará', country:'Brasil', region:'Americas', rank:81, programs:['Bach','MSc','PhD'], site:'ufc.br' },
    { id:'inst-082', name:'UFPR — Univ. Federal Paraná', country:'Brasil', region:'Americas', rank:82, programs:['Bach','MSc','PhD'], site:'ufpr.br' },
    { id:'inst-083', name:'UFBA — Univ. Federal Bahia', country:'Brasil', region:'Americas', rank:83, programs:['Bach','MSc','PhD'], site:'ufba.br' },
    { id:'inst-084', name:'UFRN — Univ. Fed. Rio Grande do Norte', country:'Brasil', region:'Americas', rank:84, programs:['Bach','MSc','PhD'], site:'ufrn.br' },
    { id:'inst-085', name:'UNB — Univ. Brasília', country:'Brasil', region:'Americas', rank:85, programs:['Bach','MSc','PhD'], site:'unb.br' },
    { id:'inst-086', name:'UFES — Univ. Federal Espírito Santo', country:'Brasil', region:'Americas', rank:86, programs:['Bach','MSc'], site:'ufes.br' },
    { id:'inst-087', name:'UFS — Univ. Federal Sergipe', country:'Brasil', region:'Americas', rank:87, programs:['Bach','MSc'], site:'ufs.br' },
    { id:'inst-088', name:'UFG — Univ. Federal Goiás', country:'Brasil', region:'Americas', rank:88, programs:['Bach','MSc'], site:'ufg.br' },
    { id:'inst-089', name:'UFAM — Univ. Federal Amazonas', country:'Brasil', region:'Americas', rank:89, programs:['Bach','MSc'], site:'ufam.edu.br' },
    { id:'inst-090', name:'UFPA — Univ. Federal Pará', country:'Brasil', region:'Americas', rank:90, programs:['Bach','MSc'], site:'ufpa.br' },
    { id:'inst-091', name:'UEM — Univ. Estadual Maringá', country:'Brasil', region:'Americas', rank:91, programs:['Bach','MSc'], site:'uem.br' },
    { id:'inst-092', name:'UDESC — Univ. Estado Santa Catarina', country:'Brasil', region:'Americas', rank:92, programs:['Bach','MSc'], site:'udesc.br' },
    { id:'inst-093', name:'PUC-SP — Pont. Univ. Católica SP', country:'Brasil', region:'Americas', rank:93, programs:['Bach','MSc'], site:'pucsp.br' },
    { id:'inst-094', name:'UNIFESP-BS — Campus Baixada Santista', country:'Brasil', region:'Americas', rank:94, programs:['Bach'], site:'unifesp.br' },
    { id:'inst-095', name:'UFRJ-Poli — Escola Anna Nery', country:'Brasil', region:'Americas', rank:95, programs:['Bach','MSc','PhD'], site:'ufrj.br' },
    { id:'inst-096', name:'USP-SP — Escola de Enfermagem', country:'Brasil', region:'Americas', rank:96, programs:['Bach','MSc','PhD'], site:'usp.br' },
    { id:'inst-097', name:'UFCSPA — Univ. Fed. Ciências Saúde RS', country:'Brasil', region:'Americas', rank:97, programs:['Bach','MSc'], site:'ufcsppa.edu.br' },
    { id:'inst-098', name:'UFSJ — Univ. Fed. São João del-Rei', country:'Brasil', region:'Americas', rank:98, programs:['Bach'], site:'ufsj.edu.br' },
    { id:'inst-099', name:'UNISC — Univ. Santa Cruz do Sul', country:'Brasil', region:'Americas', rank:99, programs:['Bach'], site:'unisc.br' },
    { id:'inst-100', name:'UECE — Univ. Estado Ceará', country:'Brasil', region:'Americas', rank:100, programs:['Bach','MSc'], site:'uece.br' },
  ],

  // ═════════════════════════════════════════════════════════════════
  // SPECIALIZATIONS WITH SKILLS BY ROLE
  // ═════════════════════════════════════════════════════════════════
  specializations: [
    {
      id:'sp-geral', name:'Enfermagem Geral', icon:'i-users',
      desc:'Atuação ampla em hospitais, clínicas e atenção primária',
      softSkills:['Comunicação','Empatia','Trabalho em equipe','Liderança','Resolução de conflitos','Adaptabilidade'],
      techSkills:['Sinais vitais','Administração de medicamentos','Curativos','Sondagens','Acessos venosos','SAE','NANDA-I','NIC','NOC','Biosegurança','Protocolos de segurança'],
      careerPath:['Técnico de Enfermagem','Enfermeiro','Enfermeiro Chefe','Coordenador','Diretor de Enfermagem'],
      marketDemand:'alta', avgSalary:'R$ 3.500 - 8.000',
    },
    {
      id:'sp-uti', name:'Enfermagem em UTI', icon:'i-pulse',
      desc:'Cuidados intensivos a pacientes críticos',
      softSkills:['Tomada de decisão rápida','Resiliência','Gestão de estresse','Comunicação com famílias','Trabalho sob pressão'],
      techSkills:['Ventilação mecânica','Hemodinâmica','Drogas vasoativas','ECG','RCP avançada','Balneamento hídrico','Sedação','Monitorização multi-paramétrica','AVP/PICC','Sepsis bundle','FASTHUG'],
      careerPath:['Enfermeiro UTI','Especialista em Terapia Intensiva','Preceptor UTI','Coordenador UTI','Gerente de Terapia Intensiva'],
      marketDemand:'altíssima', avgSalary:'R$ 5.000 - 12.000',
    },
    {
      id:'sp-neonatal', name:'Enfermagem Neonatal', icon:'i-users',
      desc:'Cuidados ao recém-nascido e prematuros',
      softSkills:['Sensibilidade','Paciência','Atenção aos detalhes','Comunicação com pais','Trabalho em equipe'],
      techSkills:['Reanimação neonatal','Apgar/Ballard/Capurro','Incubadora',' Fototerapia','CPAP neonatal','Acesso umbilical','Nutrição parenteral','Kangaroo','Triagem neonatal'],
      careerPath:['Enfermeiro Neonatal','Especialista Neonatal','Preceptor UTIN','Coordenador UTIN','Consultor em Neonatologia'],
      marketDemand:'alta', avgSalary:'R$ 4.500 - 10.000',
    },
    {
      id:'sp-ped', name:'Enfermagem Pediátrica', icon:'i-users',
      desc:'Cuidados a crianças e adolescentes',
      softSkills:['Paciência','Ludicidade','Comunicação com crianças','Empatia familiar','Criatividade'],
      techSkills:['Calculadora pediátrica','Glasgow pediátrico','FLACC/Wong-Baker','PEWS','Acesso venoso pediátrico','Dosagem por peso','Triagem neonatal','Vacinação','Desenvolvimento infantil'],
      careerPath:['Enfermeiro Pediátrico','Especialista Pediátrica','Preceptor','Coordenador Pediatria'],
      marketDemand:'alta', avgSalary:'R$ 4.000 - 9.000',
    },
    {
      id:'sp-obst', name:'Enfermagem Obstétrica', icon:'i-users',
      desc:'Cuidados pré-natal, parto e puerpério',
      softSkills:['Sensibilidade','Comunicação','Calma sob pressão','Empoderamento feminino','Respeito cultural'],
      techSkills:['Pré-natal','Parto humanizado','Bishop','MEOWS','Amamentação','Puerpério','Emergências obstétricas','Cardiotocografia','Episiorrafia'],
      careerPath:['Enfermeiro Obstetra','Enfermeira Parteira','Coordenador Maternidade','Consultor em Saúde da Mulher'],
      marketDemand:'alta', avgSalary:'R$ 4.000 - 9.500',
    },
    {
      id:'sp-psiq', name:'Enfermagem Psiquiátrica', icon:'i-brain',
      desc:'Saúde mental e cuidados psiquiátricos',
      softSkills:['Escuta ativa','Paciência','Contenção emocional','Empatia','Comunicação não-violenta','Resiliência'],
      techSkills:['CIWA-Ar','Hamilton','GAD-7','PHQ-9','Contenção química/física','Escala de suicídio','Terapia cognitiva','Gestão de crises','Legislação psiquiátrica'],
      careerPath:['Enfermeiro Psiquiátrico','Especialista em Saúde Mental','Coordenador de Unidade Psiquiátrica','Consultor em Saúde Mental'],
      marketDemand:'média', avgSalary:'R$ 4.000 - 8.500',
    },
    {
      id:'sp-geron', name:'Enfermagem Gerontológica', icon:'i-users',
      desc:'Cuidados ao idoso e geriatria',
      softSkills:['Paciência','Empatia','Respeito à autonomia','Comunicação','Observação'],
      techSkills:['Katz','Lawton','Barthel','Mini-Mental','GDS','Cornell','Fragilidade Edmonton','Fall risk','Geriátrico','Demências','Polifarmácia'],
      careerPath:['Enfermeiro Gerontológico','Especialista Geriatria','Coordenador ILPI','Consultor Gerontológico'],
      marketDemand:'crescente', avgSalary:'R$ 4.000 - 8.500',
    },
    {
      id:'sp-saudepub', name:'Enfermagem em Saúde Pública', icon:'i-shield',
      desc:'Atenção primária, vigilância e saúde coletiva',
      softSkills:['Liderança comunitária','Comunicação','Educação em saúde','Visão sistêmica','Trabalho intersectorial'],
      techSkills:['SUS','ESF','PSE','Vigilância epidemiológica','SINAN','Calendário vacinal','Notificações compulsórias','Vigilância sanitária','PNAB','eSUS'],
      careerPath:['Enfermeiro ESF','Enfermeiro de Vigilância','Coordenador de UBS','Gestor Municipal de Saúde'],
      marketDemand:'alta', avgSalary:'R$ 3.500 - 8.000',
    },
    {
      id:'sp-onco', name:'Enfermagem Oncológica', icon:'i-pulse',
      desc:'Cuidados a pacientes com câncer',
      softSkills:['Empatia','Comunicação sobre prognóstico','Resiliência','Cuidados paliativos','Suporte familiar'],
      techSkills:['Quimioterapia','Manejo de efeitos','Port-a-cath','PICC','Controle de dor','ECOG','Karnofsky','Cuidados paliativos','BPS','MASCC'],
      careerPath:['Enfermeiro Oncológico','Especialista Oncologia','Coordenador Oncologia','Consultor em Cuidados Paliativos'],
      marketDemand:'crescente', avgSalary:'R$ 5.000 - 11.000',
    },
    {
      id:'sp-emerg', name:'Enfermagem em Emergência', icon:'i-pulse',
      desc:'Atendimento pré-hospitalar e emergências',
      softSkills:['Decisão rápida','Calma sob pressão','Liderança','Comunicação','Resiliência'],
      techSkills:['Manchester','NEWS2','MEWS','RCP','ATLS/ACLS','Trauma','FAST','Intubação','Cricotireoidostomia','Toracostomia','Drogas de emergência'],
      careerPath:['Enfermeiro de Emergência','Especialista em Urgência','Preceptor SAMU','Coordenador de Emergência'],
      marketDemand:'altíssima', avgSalary:'R$ 4.500 - 10.000',
    },
    {
      id:'sp-cirurg', name:'Enfermagem Cirúrgica', icon:'i-shield',
      desc:'Centro cirúrgico e recuperação anestésica',
      softSkills:['Precisão','Concentração','Trabalho em equipe','Comunicação','Organização'],
      techSkills:['Asepsia','Esterilização','Aldrete','ASA','Posicionamento cirúrgico','ELPO','Contagem de compressos','Anestesia','Recuperação anestésica','Cirurgia segura OMS'],
      careerPath:['Enfermeiro CC','Especialista Centro Cirúrgico','Preceptor CC','Coordenador CC'],
      marketDemand:'alta', avgSalary:'R$ 4.500 - 9.500',
    },
    {
      id:'sp-gestao', name:'Gestão em Enfermagem', icon:'i-trend',
      desc:'Administração, liderança e gestão de serviços',
      softSkills:['Liderança','Gestão de pessoas','Negociação','Visão estratégica','Comunicação','Mentoria'],
      techSkills:['Dimensionamento','Fugulin','KPIs','Auditoria','CQI','Lean','Six Sigma','Gestão de processos','Legislação trabalhista','COFEN/COREN','Protocolos institucionais'],
      careerPath:['Enfermeiro Supervisor','Coordenador','Gerente','Diretor Técnico','Diretor de Enfermagem'],
      marketDemand:'alta', avgSalary:'R$ 8.000 - 20.000',
    },
  ],

  // ═════════════════════════════════════════════════════════════════
  // LEARNING PATHS (curriculum from top institutions)
  // ═════════════════════════════════════════════════════════════════
  learningPaths: [
    {
      id:'lp-fundamentos', name:'Fundamentos de Enfermagem', level:'Iniciante', hours:120,
      modules: [
        { title:'História e Filosofia da Enfermagem', topics:['Origens','Florence Nightingale','COFEN/COREN','Ética profissional'], resources:['artigo.html?id=hist','slides.html?id=hist'] },
        { title:'Anatomia e Fisiologia', topics:['Sistemas corporais','Homeostase','Semiologia'], resources:['infografico.html?id=anat'] },
        { title:'Semiotécnica e Semologia', topics:['Exame físico','Sinais vitais','Ausculta','Palpação','Percussão'], resources:['apgar.html','escala-de-glasgow.html'] },
        { title:'Processo de Enfermagem (SAE)', topics:['5 etapas','NANDA-I','NIC','NOC','Documentação'], resources:['sae.html','diagnosticosnanda.html'] },
        { title:'Farmacologia Básica', topics:['Vias de administração','9 certos','Cálculo de dose','Diluição','LASA'], resources:['medicamentos.html','gotejamento.html'] },
        { title:'Biosegurança', topics:['PPE','Descarte de resíduos','Acidentes biológicos','Higienização'], resources:['checklist.html?id=bio'] },
      ]
    },
    {
      id:'lp-clinico', name:'Prática Clínica Avançada', level:'Intermediário', hours:200,
      modules: [
        { title:'Avaliação Neurológica', topics:['Glasgow','FOUR','NIHSS','FAST','Cincinnati'], resources:['escala-de-glasgow.html','four.html'] },
        { title:'Avaliação Cardiovascular', topics:['ECG','CHA2DS2-VASc','HAS-BLED','Heart Score'], resources:['cha2ds2vasc.html'] },
        { title:'Avaliação Respiratória', topics:['Oxigenoterapia','Ventilação','Downes','Silverman'], resources:['downes.html'] },
        { title:'Avaliação de Risco', topics:['Braden','Morse','Downton','Waterlow','Caprini'], resources:['escala-de-braden.html','escala-de-morse.html'] },
        { title:'Gestão de Dor', topics:['Escala numérica','FLACC','Wong-Baker','BPS','PAINAD'], resources:['escalanumerica.html','flacc.html'] },
        { title:'Triagem e Emergência', topics:['Manchester','NEWS2','MEWS','PEWS','MEOWS'], resources:['manchester.html','news2.html'] },
      ]
    },
    {
      id:'lp-gestao', name:'Gestão e Liderança', level:'Avançado', hours:80,
      modules: [
        { title:'Dimensionamento de Pessoal', topics:['Resolução 543/2017','Cálculo','Fugulin'], resources:['dimensionamento.html','fugulin.html'] },
        { title:'Qualidade e Segurança', topics:['IPSG','Acreditação','CQI','Lean'], resources:['checklist.html?id=ipsg'] },
        { title:'Auditoria', topics:['Conformidade','Indicadores','Relatórios'], resources:[] },
        { title:'Liderança em Enfermagem', topics:['Mentoria','Coaching','Gestão de conflitos'], resources:[] },
      ]
    },
    {
      id:'lp-uti', name:'Especialização em Terapia Intensiva', level:'Avançado', hours:360,
      modules: [
        { title:'Sepsis Bundle', topics:['SIRS','SOFA','qSOFA','Culturas','Antibiótico empírico'], resources:['sofa.html','qsofa.html'] },
        { title:'Suporte Hemodinâmico', topics:['Pressão arterial invasiva','Swan-Ganz','Débito cardíaco','Drogas vasoativas'], resources:[] },
        { title:'Ventilação Mecânica', topics:['Modos ventilatórios','PVR','Desmame','Extubação'], resources:[] },
        { title:'FASTHUG BID', topics:['Feeding','Analgesia','Sedação','Tromboprofilaxia','Cabeceira','Úlcera','Glicemia'], resources:['escala-de-braden.html'] },
        { title:'Nefrologia Intensiva', topics:['TFR/TFSH','Diálise','Equilíbrio ácido-base'], resources:[] },
      ]
    },
  ],

  // ═════════════════════════════════════════════════════════════════
  // SAMPLE JOB LISTINGS (scraped data will be appended)
  // ═════════════════════════════════════════════════════════════════
  jobs: [
    { id:'job-001', title:'Enfermeiro UTI Adulto', inst:'Hospital Sírio-Libanês', city:'São Paulo, SP', type:'CLT', salary:'R$ 7.000 - 10.000', spec:'sp-uti', reqs:['Coren-SP','Experiência UTI','PALS ou ACLS'], source:'Vagas.com', posted:'2 dias atrás', url:'#' },
    { id:'job-002', title:'Enfermeiro Neonatal', inst:'Hospital Albert Einstein', city:'São Paulo, SP', type:'CLT', salary:'R$ 6.500 - 9.500', spec:'sp-neonatal', reqs:['Coren-SP','Especialização Neonatal','NRP'], source:'LinkedIn', posted:'1 dia atrás', url:'#' },
    { id:'job-003', title:'Enfermeiro de Emergência', inst:'Hospital Municipal', city:'Rio de Janeiro, RJ', type:'Plantão', salary:'R$ 5.500 - 8.000', spec:'sp-emerg', reqs:['Coren-RJ','ACLS','ATLS'], source:'Catho', posted:'3 dias atrás', url:'#' },
    { id:'job-004', title:'Enfermeiro Gestor', inst:'Rede D\'Or', city:'Belo Horizonte, MG', type:'CLT', salary:'R$ 9.000 - 15.000', spec:'sp-gestao', reqs:['Coren-MG','MBA ou MSc','5+ anos gestão'], source:'InfoJobs', posted:'5 dias atrás', url:'#' },
    { id:'job-005', title:'Enfermeiro Centro Cirúrgico', inst:'Hospital Alemão Oswaldo Cruz', city:'São Paulo, SP', type:'CLT', salary:'R$ 5.500 - 8.500', spec:'sp-cirurg', reqs:['Coren-SP','Especialização CC','Cirurgia Segura OMS'], source:'Vagas.com', posted:'1 semana atrás', url:'#' },
    { id:'job-006', title:'Enfermeiro Saúde Pública — ESF', inst:'Prefeitura Municipal', city:'Curitiba, PR', type:'Concurso', salary:'R$ 4.500 - 6.500', spec:'sp-saudepub', reqs:['Coren-PR','Experiência ESF','Concurso público'], source:'Concurso', posted:'1 semana atrás', url:'#' },
    { id:'job-007', title:'Enfermeiro Oncológico', inst:'Instituto do Câncer', city:'São Paulo, SP', type:'CLT', salary:'R$ 6.000 - 10.000', spec:'sp-onco', reqs:['Coren-SP','Especialização Oncologia','Manejo quimio'], source:'LinkedIn', posted:'4 dias atrás', url:'#' },
    { id:'job-008', title:'Enfermeira Obstetra', inst:'Maternidade Municipal', city:'Recife, PE', type:'Plantão', salary:'R$ 4.500 - 7.000', spec:'sp-obst', reqs:['Coren-PE','Especialização Obstétrica'], source:'Catho', posted:'2 dias atrás', url:'#' },
  ],

  // ═════════════════════════════════════════════════════════════════
  // FREE COURSES (scraped data will be appended)
  // ═════════════════════════════════════════════════════════════════
  courses: [
    { id:'course-001', title:'Fundamentos de Enfermagem', inst:'Fiocruz', platform:'Fiocampus', duration:'40h', lang:'PT-BR', area:'Fundamentos', url:'#', free:true },
    { id:'course-002', title:'Atenção Básica e Saúde da Família', inst:'UNASUS', platform:'UNASUS', duration:'60h', lang:'PT-BR', area:'Saúde Pública', url:'#', free:true },
    { id:'course-003', title:'Vigilância em Saúde', inst:'Fiocruz', platform:'Fiocampus', duration:'30h', lang:'PT-BR', area:'Saúde Pública', url:'#', free:true },
    { id:'course-004', title:'COVID-19: Capacitação para Enfermeiros', inst:'OMS', platform:'OpenWHO', duration:'6h', lang:'PT-BR', area:'Emergência', url:'#', free:true },
    { id:'course-005', title:'Global Health Essentials', inst:'Karolinska Institutet', platform:'edX', duration:'30h', lang:'Inglês', area:'Saúde Global', url:'#', free:true },
    { id:'course-006', title:'Nursing Care in the Community', inst:'University of Toronto', platform:'Coursera', duration:'40h', lang:'Inglês', area:'Saúde Pública', url:'#', free:true },
    { id:'course-007', title:'Palliative Care Always', inst:'Stanford University', platform:'Coursera', duration:'20h', lang:'Inglês', area:'Paliativos', url:'#', free:true },
    { id:'course-008', title:'Anatomy: Know Your Abdomen', inst:'University of Leeds', platform:'FutureLearn', duration:'4h', lang:'Inglês', area:'Anatomia', url:'#', free:true },
    { id:'course-009', title:'Gestão em Saúde', inst:'ENSP-Fiocruz', platform:'Fiocampus', duration:'50h', lang:'PT-BR', area:'Gestão', url:'#', free:true },
    { id:'course-010', title:'Human Nutrition', inst:'Harvard University', platform:'edX', duration:'12h', lang:'Inglês', area:'Nutrição', url:'#', free:true },
    { id:'course-011', title:'Saúde Mental na Atenção Básica', inst:'UNASUS', platform:'UNASUS', duration:'45h', lang:'PT-BR', area:'Psiquiatria', url:'#', free:true },
    { id:'course-012', title:'Patient Safety', inst:'WHO', platform:'OpenWHO', duration:'8h', lang:'PT-BR', area:'Segurança', url:'#', free:true },
    { id:'course-013', title:'Cuidados de Enfermagem em UTI', inst:'USP', platform:'Coursera', duration:'30h', lang:'PT-BR', area:'UTI', url:'#', free:true },
    { id:'course-014', title:'Infection Prevention and Control', inst:'London School of Hygiene', platform:'Coursera', duration:'20h', lang:'Inglês', area:'Infecção', url:'#', free:true },
    { id:'course-015', title:'Ética em Enfermagem', inst:'COFEN', platform:'COFEN Online', duration:'10h', lang:'PT-BR', area:'Ética', url:'#', free:true },
    { id:'course-016', title:'Sistematização da Assistência de Enfermagem', inst:'UNIFESP', platform:'YouTube', duration:'4h', lang:'PT-BR', area:'SAE', url:'#', free:true },
  ],

  // ═════════════════════════════════════════════════════════════════
  // ARTICLES BY SPECIALIZATION
  // ═════════════════════════════════════════════════════════════════
  articles: [
    { id:'art-001', spec:'sp-neonatal', title:'O Índice de Apgar: História e Evolução', readTime:'8 min', evidence:'GRADE A', url:'artigo.html?id=art-001' },
    { id:'art-002', spec:'sp-neonatal', title:'Interpretação Clínica do Escore de Apgar', readTime:'12 min', evidence:'GRADE B', url:'artigo.html?id=art-002' },
    { id:'art-003', spec:'sp-uti', title:'Sepsis Bundle: O Papel do Enfermeiro', readTime:'15 min', evidence:'GRADE A', url:'artigo.html?id=sepsis' },
    { id:'art-004', spec:'sp-uti', title:'FASTHUG BID na Prática de UTI', readTime:'10 min', evidence:'GRADE B', url:'artigo.html?id=fasthug' },
    { id:'art-005', spec:'sp-emerg', title:'Triagem de Manchester: Como Funciona', readTime:'12 min', evidence:'GRADE A', url:'artigo.html?id=manchester' },
    { id:'art-006', spec:'sp-gestao', title:'Dimensionamento de Enfermagem: Resolução 543/2017', readTime:'20 min', evidence:'Normativo', url:'artigo.html?id=dim' },
    { id:'art-007', spec:'sp-gestao', title:'Indicadores de Qualidade em Enfermagem', readTime:'14 min', evidence:'GRADE B', url:'artigo.html?id=kpi' },
    { id:'art-008', spec:'sp-onco', title:'Cuidados Paliativos: Quando Iniciar', readTime:'10 min', evidence:'GRADE A', url:'artigo.html?id=pal' },
    { id:'art-009', spec:'sp-psiq', title:'Gestão de Crises em Saúde Mental', readTime:'12 min', evidence:'GRADE B', url:'artigo.html?id=crise' },
    { id:'art-010', spec:'sp-geron', name:'Geriatria', title:'Fragilidade no Idoso: Como Avaliar', readTime:'10 min', evidence:'GRADE A', url:'artigo.html?id=frag' },
    { id:'art-011', spec:'sp-obst', title:'Parto Humanizado: Evidência e Prática', readTime:'16 min', evidence:'GRADE A', url:'artigo.html?id=parto' },
    { id:'art-012', spec:'sp-cirurg', title:'Cirurgia Segura: Checklist OMS', readTime:'8 min', evidence:'GRADE A', url:'artigo.html?id=surgical' },
  ],

  // ═════════════════════════════════════════════════════════════════
  // CONCURSOS PÚBLICOS — Editais abertos e previstos
  // Fonte: QConcursos, Gran Cursos, Estratégia, Prepara Enfermagem
  // ═════════════════════════════════════════════════════════════════
  concursos: [
    // Abertos
    { id:'conc-001', inst:'Prefeitura de Ipatinga — MG', region:'Sudeste', uf:'MG', status:'aberto', deadline:'17/07/2026', examDate:'A definir', vacancies:138, salary:'R$ 6.873,50', positions:['Enfermeiro','Enfermeiro ESF','Técnico de Enfermagem ESF'], board:'IBFC', url:'#', daysLeft:12 },
    { id:'conc-002', inst:'Prefeitura de Bom Repouso — MG', region:'Sudeste', uf:'MG', status:'aberto', deadline:'20/07/2026', examDate:'A definir', vacancies:18, salary:'R$ 5.229,00', positions:['Enfermeiro','Enfermeiro ESF','Técnico de Enfermagem','Técnico ESF'], board:'AOCP', url:'#', daysLeft:15 },
    { id:'conc-003', inst:'Prefeitura de Congonhal — MG', region:'Sudeste', uf:'MG', status:'aberto', deadline:'31/07/2026', examDate:'A definir', vacancies:12, salary:'R$ 3.822,07', positions:['Enfermeiro','Técnico de Enfermagem'], board:'FUMARC', url:'#', daysLeft:26 },
    { id:'conc-004', inst:'Prefeitura de Paracatu — MG', region:'Sudeste', uf:'MG', status:'aberto', deadline:'15/07/2026', examDate:'A definir', vacancies:0, salary:'R$ 5.944,23', positions:['Enfermeiro','Técnico de Enfermagem'], board:'IBFC', url:'#', daysLeft:10, cadastroReserva:true },
    { id:'conc-005', inst:'Prefeitura de Matozinhos — MG', region:'Sudeste', uf:'MG', status:'aberto', deadline:'07/07/2026', examDate:'A definir', vacancies:2, salary:'R$ 4.280,23', positions:['Fiscal Sanitário-Enfermagem'], board:'AOCP', url:'#', daysLeft:2 },
    { id:'conc-006', inst:'EBSERH — Hospital Universitário', region:'Nacional', uf:'Nacional', status:'aberto', deadline:'30/07/2026', examDate:'Setembro 2026', vacancies:340, salary:'R$ 4.600,00', positions:['Enfermeiro','Técnico de Enfermagem'], board:'Cebraspe', url:'#', daysLeft:25 },
    { id:'conc-007', inst:'COFEN — Conselho Federal de Enfermagem', region:'Nacional', uf:'Nacional', status:'aberto', deadline:'15/08/2026', examDate:'Outubro 2026', vacancies:13, salary:'R$ 13.000,00', positions:['Enfermeiro Fiscal','Analista Técnico','Coordenador'], board:'FGV', url:'#', daysLeft:41 },
    { id:'conc-008', inst:'Prefeitura de São Gonçalo — RJ', region:'Sudeste', uf:'RJ', status:'aberto', deadline:'25/07/2026', examDate:'A definir', vacancies:85, salary:'R$ 4.500,00', positions:['Enfermeiro ESF','Técnico de Enfermagem'], board:'FJG', url:'#', daysLeft:20 },

    // Previstos
    { id:'conc-009', inst:'Prefeitura de Belo Horizonte — MG', region:'Sudeste', uf:'MG', status:'previsto', deadline:'A definir', examDate:'Novembro 2026', vacancies:500, salary:'R$ 5.500,00', positions:['Enfermeiro','Técnico de Enfermagem'], board:'A definir', url:'#', daysLeft:null },
    { id:'conc-010', inst:'Governo do Estado de São Paulo', region:'Sudeste', uf:'SP', status:'previsto', deadline:'A definir', examDate:'Dezembro 2026', vacancies:1200, salary:'R$ 5.800,00', positions:['Enfermeiro','Técnico de Enfermagem'], board:'Vunesp', url:'#', daysLeft:null },
    { id:'conc-011', inst:'Governo do Estado do Rio de Janeiro', region:'Sudeste', uf:'RJ', status:'previsto', deadline:'A definir', examDate:'Janeiro 2027', vacancies:800, salary:'R$ 5.200,00', positions:['Enfermeiro','Técnico de Enfermagem'], board:'Cetro', url:'#', daysLeft:null },
    { id:'conc-012', inst:'Prefeitura de Curitiba — PR', region:'Sul', uf:'PR', status:'previsto', deadline:'A definir', examDate:'Outubro 2026', vacancies:200, salary:'R$ 5.000,00', positions:['Enfermeiro ESF','Técnico de Enfermagem'], board:'NC-UFPR', url:'#', daysLeft:null },
    { id:'conc-013', inst:'Governo do Estado da Bahia', region:'Nordeste', uf:'BA', status:'previsto', deadline:'A definir', examDate:'Novembro 2026', vacancies:600, salary:'R$ 4.800,00', positions:['Enfermeiro','Técnico de Enfermagem'], board:'UEFS', url:'#', daysLeft:null },
    { id:'conc-014', inst:'Prefeitura de Fortaleza — CE', region:'Nordeste', uf:'CE', status:'previsto', deadline:'A definir', examDate:'Setembro 2026', vacancies:150, salary:'R$ 4.500,00', positions:['Enfermeiro ESF','Técnico'], board:'Esaf', url:'#', daysLeft:null },
    { id:'conc-015', inst:'Governo do Distrito Federal', region:'Centro-Oeste', uf:'DF', status:'previsto', deadline:'A definir', examDate:'Outubro 2026', vacancies:300, salary:'R$ 6.000,00', positions:['Enfermeiro','Técnico de Enfermagem'], board:'Cebraspe', url:'#', daysLeft:null },
    { id:'conc-016', inst:'Governo do Estado do Amazonas', region:'Norte', uf:'AM', status:'previsto', deadline:'A definir', examDate:'Novembro 2026', vacancies:250, salary:'R$ 4.700,00', positions:['Enfermeiro','Técnico'], board:'FGV', url:'#', daysLeft:null },
    { id:'conc-017', inst:'Marinha do Brasil — Saúde', region:'Nacional', uf:'Nacional', status:'previsto', deadline:'A definir', examDate:'Agosto 2026', vacancies:40, salary:'R$ 7.500,00', positions:['Enfermeiro Militar','Técnico'], board:'DPC', url:'#', daysLeft:null },
    { id:'conc-018', inst:'Exército Brasileiro — Saúde', region:'Nacional', uf:'Nacional', status:'previsto', deadline:'A definir', examDate:'Setembro 2026', vacancies:60, salary:'R$ 8.000,00', positions:['Enfermeiro Militar'], board:'EsFN', url:'#', daysLeft:null },
  ],

  // Regiões do Brasil
  regioes: ['Nacional','Centro-Oeste','Norte','Nordeste','Sudeste','Sul'],
  ufs: ['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO'],

  // Matérias cobradas em concursos de enfermagem
  materiasConcurso: [
    { name:'Fundamentos de Enfermagem', weight:25, topics:['Semiologia','Sinais vitais','Administração de medicamentos','Curativos','Sondagens','Acessos venosos'] },
    { name:'SAE — Sistematização da Assistência', weight:15, topics:['NANDA-I','NIC','NOC','Processo de enfermagem','Documentação'] },
    { name:'Saúde Pública / SUS', weight:20, topics:['Lei 8080','Lei 8142','NOB/SUS','PNAB','ESF','Vigilância epidemiológica','SINAN','Calendário vacinal'] },
    { name:'Legislação Profissional', weight:10, topics:['Lei 7498/86','Decreto 94406/87','Resoluções COFEN','Código de Ética','Resolução 543/2017'] },
    { name:'Clínica Médica', weight:15, topics:['Cardiologia','Pneumologia','Gastroenterologia','Nefrologia','Endocrinologia','Neurologia'] },
    { name:'Clínica Cirúrgica', weight:10, topics:['Pré/intra/pós-operatório','Centro cirúrgico','Asepsia','Cicatrização','Drenos'] },
    { name:'Emergência / UTI', weight:10, topics:['RCP','Triagem Manchester','Drogas vasoativas','Ventilação mecânica','Sepsis'] },
    { name:'Ética e Bioética', weight:5, topics:['Princípios bioéticos','Consentimento','Sigilo','Resolução 311/2007'] },
  ],
  ],
};
