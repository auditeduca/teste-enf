/* =====================================================================
   Personalização por Perfil — Calculadoras de Enfermagem
   Adapta dashboard, ferramentas, trilhas e conteúdo por audiência
   ===================================================================== */
(function(){
  'use strict';

  // === Dados de perfis (do NKOS 2026) ===
  const profiles = {
    student: {
      name: 'Estudante',
      level: 'Iniciante',
      priorityModules: ['educacao','simulados','flashcards','trilhas'],
      objectives: [
        'Desenvolver competências em fundamentos clínicos',
        'Integrar ferramentas NKOS 2026 ao fluxo de aprendizado',
        'Praticar com simulados e questões de concurso',
        'Memorizar conceitos com flashcards interativos'
      ],
      tools: [
        {name:'Glasgow',desc:'Escala de Coma',url:'glasgow.html'},
        {name:'Braden',desc:'Risco de Úlcera por Pressão',url:'braden.html'},
        {name:'Morse',desc:'Risco de Queda',url:'morse.html'},
        {name:'APGAR',desc:'Avaliação Neonatal',url:'apgar.html'},
        {name:'IMC',desc:'Índice de Massa Corporal',url:'imc.html'},
        {name:'Biblioteca de Provas',desc:'Simulados e questões',url:'biblioteca-provas.html'},
      ],
      modules: [
        {name:'Fundamentos de Enfermagem',desc:'9 lições · 12h estimadas'},
        {name:'Sinais Vitais',desc:'6 lições · Iniciante'},
        {name:'Cálculo de Medicações',desc:'8 lições · Essencial'},
        {name:'Trilha de Conhecimento',desc:'Percursos formativos',url:'trilha-conhecimento.html'},
      ],
      path: {
        title: 'Fundamentos Clínicos',
        desc: 'Comece com as escalas fundamentais e cálculos básicos. A trilha estudante prioriza aprendizado progressivo, simulados e fixação de conceitos.',
        tools: ['GCS','Braden','Morse','APGAR','IMC']
      }
    },
    professional: {
      name: 'Enfermeiro Assistencial',
      level: 'Avançado',
      priorityModules: ['calculadoras','escalas','protocolos','dual_check'],
      objectives: [
        'Realizar cálculos clínicos com precisão e segurança',
        'Aplicar escalas e protocolos institucionais',
        'Executar dual check em medicações de alto alerta',
        'Documentar SAE com NANDA, NIC e NOC'
      ],
      tools: [
        {name:'Gotejamento',desc:'Cálculo de infusão',url:'gotejamento.html'},
        {name:'Dosagem',desc:'Cálculo de medicação',url:'medicamentos.html'},
        {name:'Gotejamento',desc:'Velocidade de infusão IV',url:'gotejamento.html'},
        {name:'SAE Wizard',desc:'Plano de cuidados NANDA/NIC/NOC',url:'sae-wizard.html'},
        {name:'SBAR',desc:'Comunicação clínica',url:'sbar.html'},
        {name:'Balanço Hídrico',desc:'Controle de fluidos',url:'balancohidrico.html'},
        {name:'APGAR',desc:'Avaliação neonatal',url:'apgar.html'},
        {name:'Bishop',desc:'Score de Bishop',url:'bishop.html'},
      ],
      modules: [
        {name:'Protocolos Institucionais',desc:'200 protocolos WHO/MS-BR'},
        {name:'Medicações de Alto Alerta',desc:'9 Rights + IPSG'},
        {name:'NANDA-I 2026',desc:'244 diagnósticos atualizados'},
        {name:'PlanoEnf',desc:'Assistente de planos de cuidado',url:'plano-enf.html'},
      ],
      path: {
        title: 'Prática Assistencial Segura',
        desc: 'Foco em cálculos precisos, escalas clínicas, protocolos institucionais e documentação SAE. O modo profissional ativa dual check e validação de segurança.',
        tools: ['Gotejamento','Dosagem','SAE','SBAR','Balanço Hídrico']
      }
    },
    manager: {
      name: 'Gestor de Enfermagem',
      level: 'Estratégico',
      priorityModules: ['indicadores','dimensionamento','compliance','relatorios'],
      objectives: [
        'Monitorar KPIs e indicadores de desempenho',
        'Realizar dimensionamento de pessoal por escala',
        'Garantir compliance com NR-01 e resoluções COFEN',
        'Gerar relatórios de produtividade e qualidade'
      ],
      tools: [
        {name:'Dimensionamento',desc:'Cálculo de pessoal',url:'dimensionamento.html'},
        {name:'Plantão Certo',desc:'Gestão de escalas',url:'plantao-certo.html'},
        {name:'Calculadora Trabalhista',desc:'Direitos trabalhistas',url:'calculo-hora-extra.html'},
        {name:'NurseGuard Pro',desc:'Gestão de riscos NR-01',url:'#'},
        {name:'NurseMetrics Pro',desc:'KPIs e indicadores',url:'#'},
        {name:'Adicional Noturno',desc:'Cálculo trabalhista',url:'adicional-noturno.html'},
      ],
      modules: [
        {name:'Compliance NR-01',desc:'Gestão de riscos ocupacionais'},
        {name:'Dimensionamento COFEN',desc:'Lei 7.498/86 e Res. 543/2017'},
        {name:'Indicadores de Qualidade',desc:'KPIs de enfermagem'},
        {name:'Relatórios Gerenciais',desc:'Produtividade e auditoria'},
      ],
      path: {
        title: 'Gestão e Governança',
        desc: 'Acesso a indicadores, dimensionamento de pessoal, compliance normativo e relatórios. O modo gestor prioriza visão estratégica e auditoria de processos.',
        tools: ['Dimensionamento','Plantão Certo','NurseGuard','NurseMetrics']
      }
    },
    academic: {
      name: 'Acadêmico / Pesquisador',
      level: 'Pesquisa',
      priorityModules: ['artigos','biblioteca','nanda','pesquisa'],
      objectives: [
        'Acessar evidência científica com grau GRADE',
        'Consultar NANDA-I, NIC e NOC atualizados',
        'Realizar revisão de literatura com referências primárias',
        'Integrar dados SNOMED CT e ICD-11'
      ],
      tools: [
        {name:'NANDA-I 2026',desc:'244 diagnósticos com evidência',url:'sae.html'},
        {name:'Biblioteca',desc:'Artigos e referências',url:'biblioteca.html'},
        {name:'Grafo Clínico',desc:'Rede de conhecimento NANDA/NIC/NOC',url:'grafo-clinico.html'},
        {name:'APGAR Evidência',desc:'Fontes primárias com DOI',url:'apgar.html'},
        {name:'NNN Linkages',desc:'1500 mapeamentos NANDA→NIC→NOC',url:'sae.html'},
        {name:'Trilha de Conhecimento',desc:'Percursos formativos',url:'trilha-conhecimento.html'},
      ],
      modules: [
        {name:'Evidência GRADE',desc:'27 entries High/Moderate/Low/Very_Low'},
        {name:'SNOMED CT / ICD-11',desc:'Mapeamento terminológico'},
        {name:'NNN Linkages',desc:'1500 conexões validadas'},
        {name:'Grafo de Conhecimento',desc:'Visualização interativa',url:'grafo-clinico.html'},
      ],
      path: {
        title: 'Pesquisa e Evidência',
        desc: 'Acesso a terminologias formais (NANDA-I, NIC, NOC, SNOMED CT, ICD-11), evidência científica com GRADE e linkages NNN validados. O modo acadêmico prioriza rigor metodológico.',
        tools: ['NANDA-I','Grafo Clínico','Biblioteca','NNN Linkages']
      }
    }
  };

  // === Onboarding questionnaires (do NKOS 2026) ===
  const questionnaires = {
    student: [
      {q:'Qual seu objetivo principal na plataforma?',opts:['Educação','Simulados','Flashcards','Trilhas']},
      {q:'Qual seu semestre atual?',opts:['1º-2º','3º-4º','5º-6º','7º-8º+']},
      {q:'Qual área você mais se interessa?',opts:['Clínica médica','UTI','Urgência','Materno-infantil']}
    ],
    professional: [
      {q:'Qual seu objetivo principal na plataforma?',opts:['Calculadoras','Escalas','Protocolos','Dual check']},
      {q:'Qual seu setor de atuação?',opts:['UTI','Emergência','Centro Cirúrgico','Enfermaria']},
      {q:'Você usa SAE na prática?',opts:['Sim, sempre','Às vezes','Raramente','Não']}
    ],
    manager: [
      {q:'Qual seu objetivo principal na plataforma?',opts:['Compliance','Governança','Relatórios','Multi-unidade']},
      {q:'Quantos enfermeiros você gerencia?',opts:['1-10','11-30','31-60','60+']},
      {q:'Você tem sistema de KPIs?',opts:['Sim, formalizado','Em implementação','Informal','Não']}
    ],
    academic: [
      {q:'Qual seu objetivo principal na plataforma?',opts:['Artigos','Biblioteca','NANDA','Pesquisa']},
      {q:'Qual seu nível de pesquisa?',opts:['Iniciação','Mestrado','Doutorado','Pós-doc']},
      {q:'Qual terminologia você mais usa?',opts:['NANDA-I','NIC','NOC','SNOMED CT']}
    ]
  };

  // === APGAR content by profile (exemplo) ===
  const apgarContent = {
    student: {
      title: 'Estudante',
      intro: 'O Escore de Apgar é uma avaliação rápida realizada no recém-nascido logo após o nascimento, nos minutos 1 e 5. Foi criado pela Dra. Virginia Apgar em 1953 e é usado mundialmente para identificar bebês que podem precisar de ajuda.',
      sections: [
        {h:'Objetivos de aprendizado',items:[
          'Compreender os 5 componentes do escore Apgar (Aparência, Pulso, Irritabilidade reflexa, Atividade, Respiração)',
          'Aprender a atribuir pontuação de 0 a 2 para cada componente',
          'Interpretar os resultados: 0-3 (crítico), 4-6 (moderado), 7-10 (normal)'
        ]},
        {h:'Erros comuns',items:[
          'Avaliar antes do minuto completo de vida',
          'Esquecer de reavaliar no 5º minuto',
          'Não registrar a pontuação no prontuário'
        ]}
      ]
    },
    professional: {
      title: 'Enfermeiro',
      intro: 'Como enfermeiro assistencial, você é responsável por realizar e interpretar o Apgar rapidamente, comunicando a equipe e documentando os resultados. A precisão da avaliação impacta diretamente as decisões de reanimação neonatal.',
      sections: [
        {h:'Algoritmo de decisão',items:[
          'Apgar 7-10: RN estável, manter observação',
          'Apgar 4-6: reassociação moderada — estimular, oxigenar, avaliar',
          'Apgar 0-3: reassociação vigorosa — chamar neonatologista imediatamente'
        ]},
        {h:'SOAP',items:[
          'S: Mãe refere — parto e tempo de gestação',
          'O: Apgar 1min=X, 5min=Y, peso, temperatura',
          'A: RN com/necessidade de reassociação',
          'P: Intervenções realizadas e plano de monitorização'
        ]}
      ]
    },
    manager: {
      title: 'Gestor',
      intro: 'O Apgar é um indicador de qualidade neonatal. Como gestor, monitore a taxa de Apgar <7 no 5º minuto como KPI institucional e garanta treinamento contínuo da equipe.',
      sections: [
        {h:'Métricas e benchmarks',items:[
          'Taxa de Apgar <7 no 5º minuto (meta WHO: <5%)',
          'Tempo médio de registro no prontuário',
          'Percentual de reanimações neonatais',
          'Adesão ao protocolo institucional'
        ]},
        {h:'Ações de melhoria',items:[
          'Treinamento trimestral em reanimação neonatal',
          'Auditoria de prontuários neonatais',
          'Implementar checklist de segurança pós-parto'
        ]}
      ]
    },
    academic: {
      title: 'Acadêmico',
      intro: 'O Apgar Score (1953) é uma das escalas mais citadas na literatura médica. Fundamentação teórica e evidência científica são essenciais para pesquisa e publicação.',
      sections: [
        {h:'Fundamentação teórica',items:[
          'Apgar V. Anesthesia & Analgesia, 1953 — validação original',
          'ACOG Committee Opinion 2015 — atualização de diretrizes',
          'WHO Guidelines on Basic Newborn Resuscitation, 2013',
          'Evidência GRADE A — recomendado em todas as diretrizes'
        ]},
        {h:'Referências',items:[
          'Apgar, V. (1953). A proposal for a new method of evaluation of the newborn infant. Anesth Analg, 32(4), 260-267.',
          'ACOG Committee Opinion No. 633. (2015). Obstet Gynecol, 125, 1080-1086.',
          'WHO. (2013). Guidelines on basic newborn resuscitation. Geneva: World Health Organization.'
        ]}
      ]
    }
  };

  // === State ===
  let selectedProfile = null;
  let onboardingAnswers = {};

  // === Init ===
  function init(){
    bindProfileCards();
    bindOnboarding();
  }

  function bindProfileCards(){
    document.querySelectorAll('.profile-card').forEach(card => {
      card.addEventListener('click', () => selectProfile(card.dataset.profile));
      card.addEventListener('keydown', (e) => {
        if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); selectProfile(card.dataset.profile); }
      });
    });
  }

  function selectProfile(profile){
    selectedProfile = profile;
    onboardingAnswers = {};

    document.querySelectorAll('.profile-card').forEach(c => {
      c.classList.remove('active');
      c.setAttribute('aria-checked','false');
    });
    const activeCard = document.querySelector(`.profile-card[data-profile="${profile}"]`);
    if(activeCard){
      activeCard.classList.add('active');
      activeCard.setAttribute('aria-checked','true');
    }

    showOnboarding(profile);
  }

  function showOnboarding(profile){
    const panel = document.getElementById('onboarding-panel');
    const container = document.getElementById('onboarding-questions');
    const qs = questionnaires[profile] || [];

    if(!qs.length){ applyProfile(profile); return; }

    container.innerHTML = qs.map((q, i) => `
      <div class="onboarding-q">
        <div class="q-text">${i+1}. ${q.q}</div>
        <div class="onboarding-options">
          ${q.opts.map(o => `<button class="onboarding-opt" data-q="${i}" data-a="${o}">${o}</button>`).join('')}
        </div>
      </div>
    `).join('');

    container.querySelectorAll('.onboarding-opt').forEach(btn => {
      btn.addEventListener('click', () => {
        const qIdx = btn.dataset.q;
        const ans = btn.dataset.a;
        onboardingAnswers[qIdx] = ans;
        container.querySelectorAll(`.onboarding-opt[data-q="${qIdx}"]`).forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
      });
    });

    panel.classList.add('show');
  }

  function bindOnboarding(){
    document.getElementById('btn-apply-profile')?.addEventListener('click', () => {
      if(selectedProfile) applyProfile(selectedProfile);
    });
    document.getElementById('btn-skip-onboarding')?.addEventListener('click', () => {
      if(selectedProfile) applyProfile(selectedProfile);
    });
  }

  function applyProfile(profile){
    const data = profiles[profile];
    if(!data) return;

    // Hide onboarding
    document.getElementById('onboarding-panel').classList.remove('show');

    // Show dashboard
    const dash = document.getElementById('profile-dashboard');
    dash.classList.add('show');

    // Path card
    document.getElementById('path-level').textContent = data.level;
    document.getElementById('path-title').textContent = data.path.title;
    document.getElementById('path-description').textContent = data.path.desc;
    document.getElementById('path-tools').innerHTML = data.path.tools.map(t =>
      `<span class="path-tool">${t}</span>`
    ).join('');

    // Priority tools
    document.getElementById('priority-tools').innerHTML = data.tools.map(t => `
      <a class="dashboard-tool-item" href="${t.url || '#'}">
        <span class="tool-dot"></span>
        <div><div class="tool-name">${t.name}</div><div class="tool-desc">${t.desc}</div></div>
      </a>
    `).join('');

    // Objectives
    document.getElementById('objectives-list').innerHTML = data.objectives.map(o => `
      <div class="dashboard-objective"><i class="fa-solid fa-circle-check"></i> ${o}</div>
    `).join('');

    // Modules
    document.getElementById('modules-list').innerHTML = data.modules.map(m => `
      <a class="dashboard-tool-item" href="${m.url || '#'}">
        <span class="tool-dot"></span>
        <div><div class="tool-name">${m.name}</div><div class="tool-desc">${m.desc}</div></div>
      </a>
    `).join('');

    // Content preview (APGAR example)
    showContentPreview(profile);

    // Scroll to dashboard
    dash.scrollIntoView({behavior:'smooth', block:'start'});
  }

  function showContentPreview(profile){
    const preview = document.getElementById('content-preview');
    const tabsContainer = document.getElementById('preview-tabs');
    const contentsContainer = document.getElementById('preview-contents');

    const profileKeys = Object.keys(apgarContent);
    tabsContainer.innerHTML = profileKeys.map((k, i) => `
      <button class="preview-tab ${k === profile ? 'active' : ''}" data-profile="${k}">${apgarContent[k].title}</button>
    `).join('');

    contentsContainer.innerHTML = profileKeys.map(k => {
      const c = apgarContent[k];
      return `<div class="preview-content ${k === profile ? 'show' : ''}" data-profile="${k}">
        <p>${c.intro}</p>
        ${c.sections.map(s => `<h4>${s.h}</h4><ul>${s.items.map(i => `<li>${i}</li>`).join('')}</ul>`).join('')}
      </div>`;
    }).join('');

    tabsContainer.querySelectorAll('.preview-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        tabsContainer.querySelectorAll('.preview-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        contentsContainer.querySelectorAll('.preview-content').forEach(c => c.classList.remove('show'));
        contentsContainer.querySelector(`.preview-content[data-profile="${tab.dataset.profile}"]`).classList.add('show');
      });
    });

    preview.style.display = 'block';
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
