/* ════════════════════════════════════════════════════════════════════
   ZEN DATA — Sala de Descompressão para Profissionais de Enfermagem
   10 artigos + áudios guiados + exercícios + recursos
   ════════════════════════════════════════════════════════════════════ */
window.ZEN_DATA = {

  // ═════════════════════════════════════════════════════════════════
  // 10 ARTIGOS — Bem-estar e Saúde Mental do Enfermeiro
  // ═════════════════════════════════════════════════════════════════
  articles: [
    {
      id:'zen-01',
      title:'Burnout em Enfermagem: Reconhecer é o Primeiro Passo',
      category:'identificacao',
      readTime:'8 min',
      evidence:'GRADE B',
      excerpt:'Síndrome de esgotamento físico e emocional. Aprenda os 3 estágios clássicos (exaustão, cinismo, ineficácia) e os sinais de alerta precoce que todo enfermeiro deveria monitorar.',
      body:[
        {type:'p', text:'O burnout não é fraqueza. É a resposta natural do corpo e da mente a uma exposição prolongada ao estresse ocupacional. Estudos indicam que 35–50% dos profissionais de enfermagem apresentam sintomas de burnout em algum momento da carreira.'},
        {type:'p', text:'Os três estágios clássicos (Maslach, 1981) são: 1) Exaustão emocional — a sensação de não ter mais nada para dar; 2) Despersonalização (cinismo) — tratar pacientes como objetos ou números; 3) Redução da realização profissional — sentir que nada do que você faz faz diferença.'},
        {type:'h2', text:'Sinais de alerta precoce'},
        {type:'list', items:[
          'Dificuldade para dormir mesmo após o plantão',
          'Irritabilidade crescente com colegas e familiares',
          'Apatia diante de situações antes emocionantes',
          'Aumento do consumo de café, energéticos ou álcool',
          'Esquecimentos frequentes na administração de medicamentos',
          'Dores de cabeça tensão e desconforto cervical recorrentes'
        ]},
        {type:'p', text:'Se você reconhece 3 ou mais sinais, pause. Não espere o colapso. O burnout é reversível quando identificado nos estágios iniciais. A Resolução COFEN 550/2017 reconhece a saúde mental do enfermeiro como questão de segurança assistencial.'},
        {type:'quote', text:'Cuidar de quem cuida não é um luxo — é uma necessidade de segurança do paciente.'},
        {type:'p', text:'Ferramentas de rastreamento: Maslach Burnout Inventory (MBI-HSS), Professional Quality of Life Scale (ProQOL). Ambas são gratuitas para uso individual e podem ser aplicadas como autoavaliação periódica.'}
      ],
      references:[
        'Maslach C, Jackson SE. MBI: Maslach Burnout Inventory. Consulting Psychologists Press; 1981.',
        'COFEN. Resolução 550/2017. Saúde mental do profissional de enfermagem.',
        'ANVISA. Segurança do paciente e cultura de cuidado ao cuidador. 2023.'
      ]
    },
    {
      id:'zen-02',
      title:'Respiração 4-7-8: Técnica de Relaxamento em 60 Segundos',
      category:'tecnicas',
      readTime:'5 min',
      evidence:'GRADE A',
      excerpt:'Técnica validada por Herbert Weil (Harvard) que ativa o sistema nervoso parassimpático em menos de um minuto. Ideal para usar entre atendimentos, na sala de repouso ou antes de dormir pós-plantão.',
      body:[
        {type:'p', text:'A respiração 4-7-8 é uma técnica derivada do pranayama yoga, adaptada pelo Dr. Andrew Weil de Harvard Medical School. Funciona ativando o nervo vago, que sinaliza ao cérebro que é seguro relaxar.'},
        {type:'h2', text:'Como executar (passo a passo)'},
        {type:'list', items:[
          'Coloque a ponta da língua no céu da boca, atrás dos dentes frontais',
          'Expire completamente pela boca (som de sopro)',
          'Feche a boca e inspire pelo nariz contando até 4',
          'Prenda a respiração contando até 7',
          'Expire pela boca contando até 8 (som de sopro)',
          'Repita o ciclo 4 vezes (total: ~60 segundos)'
        ]},
        {type:'p', text:'A proporção 4:7:8 é o que faz a diferença. A expiração longa (8) força o diafragma a liberar tensão acumulada, enquanto a pausa (7) permite a troca gasosa completa nos alvéolos.'},
        {type:'p', text:'Quando usar: entre atendimentos de alta complexidade, antes de procedimentos invasivos, ao acordar no meio da noite, ao sentir irritação crescendo, no trânsito de volta para casa.'},
        {type:'quote', text:'A respiração é a única função autônoma que podemos controlar voluntariamente. Use isso ao seu favor.'},
        {type:'p', text:'Estudo de Cochrane (2023) confirma que técnicas respiratórias reduzem cortisol salivar em 23% após 5 minutos de prática. Não é placebo — é fisiologia.'}
      ],
      references:[
        'Weil A. Breathing: The Master Key to Self-Healing. Sounds True; 2005.',
        'Cochrane Review. Relaxation techniques for stress anxiety. 2023.',
        'Perciavalle V, et al. The role of deep breathing on stress. Neurol Sci. 2017.'
      ]
    },
    {
      id:'zen-03',
      title:'O Plantão de 12h e o Ciclo Circadiano: Como Proteger Seu Sono',
      category:'sono',
      readTime:'12 min',
      evidence:'GRADE A',
      excerpt:'O enfermeiro de plantão noturno vive em fuso horário permanente com seu próprio corpo. Entenda a cronobiologia do sono e estratégias baseadas em evidência para recuperar o descanso.',
      body:[
        {type:'p', text:'O ser humano é uma espécie diurna. O enfermeiro noturno pede ao seu corpo que faça algo进化 contrário a milhões de anos de evolução. A melatonina — hormônio do sono — começa a subir às 21h e pico às 3h da manhã. Exatamente quando você está no pico do plantão.'},
        {type:'h2', text:'Estratégias de higiene do sono pós-plantão'},
        {type:'list', items:[
          'Use óculos de sol escuros na saída do hospital (bloqueia luz que reinicia o ciclo circadiano)',
          'Mantenha o quarto escuro com blackout e temperatura entre 18-20°C',
          'Evite telas 30 min antes de dormir (luz azul suprime melatonina)',
          'Considere melatonina 0,5-3mg 30 min antes de dormir (consulte seu médico)',
          'Mantenha horário consistente mesmo nos dias de folga (variabilidade < 2h)',
          'Cafeína: última dose 6h antes de dormir (meia-vida: 5-6h)'
        ]},
        {type:'h2', text:'A soneca estratégica'},
        {type:'p', text:'Estudo de Rogers (2004) com 392 enfermeiros mostrou que sonecas de 20-30 minutos durante o plantão reduziram erros de medicação em 34%. A soneca não é preguiça — é segurança do paciente.'},
        {type:'p', text:'Janela ideal: 20 minutos (evita inércia do sono) ou 90 minutos (um ciclo completo de REM). Nunca entre 30-60 minutos (sono profundo = despertar confuso).'},
        {type:'quote', text:'Sono não é tempo perdido. É manutenção preventiva do instrumento mais importante do hospital: você.'},
        {type:'p', text:'Sinais de privação crônica de sono: micro-sono (3-15 segundos de blackout mental), alucinações periféricas, lapsos de memória de curto prazo, tremores de mão. Se você apresenta qualquer um desses, não está descansando o suficiente.'}
      ],
      references:[
        'Rogers AE, et al. The working hours of hospital staff nurses and patient safety. Health Aff. 2004.',
        'AASM. Sleep and the night shift worker. J Clin Sleep Med. 2015.',
        'Geiger-Brown J, et al. Sleep, sleepiness, fatigue, and performance of 12-hour shift nurses. Chronobiol Int. 2012.'
      ]
    },
    {
      id:'zen-04',
      title:'Mindfulness na Enfermagem: Estar Presente em Cada Atendimento',
      category:'tecnicas',
      readTime:'10 min',
      evidence:'GRADE A',
      excerpt:'Mindfulness não é espiritualidade — é treino de atenção. Programas MBSR aplicados a enfermeiros reduziram burnout em 38% e aumentaram satisfação profissional em 27% (meta-análise de 2023).',
      body:[
        {type:'p', text:'Mindfulness-Based Stress Reduction (MBSR) foi desenvolvido por Jon Kabat-Zinn na Universidade de Massachusetts em 1979. Para enfermagem, significa prestar atenção ao momento presente — o paciente à sua frente — sem julgamento e sem a mente dividida entre 10 tarefas futuras.'},
        {type:'h2', text:'Prática de 3 minutos para usar entre atendimentos'},
        {type:'list', items:[
          'Minuto 1 — Consciência: Pare. Sinta seus pés no chão. Observe sua respiração sem alterá-la.',
          'Minuto 2 — Atenção: Expanda a consciência para o corpo todo. Onde há tensão? Ombros? Mandíbula? Sinta e solte.',
          'Minuto 3 — Intenção: Traga à mente o próximo paciente. Diga mentalmente: "Vou estar presente para esta pessoa."'
        ]},
        {type:'p', text:'A prática parece simples demais para funcionar. Mas a neurociência mostra que 3 minutos de mindfulness ativam o córtex pré-frontal (decisão) e reduzem a amígdala (reação de medo). É um interruptor neural.'},
        {type:'h2', text:'Resultados em enfermagem'},
        {type:'p', text:'Meta-análise de 18 estudos (n=1.247 enfermeiros): redução de 38% em exaustão emocional, aumento de 27% em satisfação profissional, melhora de 22% em empatia. Não é mágica — é treino consistente.'},
        {type:'quote', text:'Entre o estímulo e a resposta, há um espaço. Nesse espaço está nosso poder de escolher. — Viktor Frankl'},
        {type:'p', text:'Apps gratuitos recomendados: Insight Timer (gratuito), Healthy Minds Program (gratuito, sem anúncios), Mindsight (criado por Dan Siegel). Todos oferecem práticas curtas específicas para profissionais de saúde.'}
      ],
      references:[
        'Kabat-Zinn J. Full Catastrophe Living. Bantam; 1990.',
        'Burton A, et al. Effect of mindfulness on nurses and patients. J Nurs Manag. 2023.',
        'Frankl VE. Man\'s Search for Meaning. Beacon Press; 1946.'
      ]
    },
    {
      id:'zen-05',
      title:'Ansiedade Antes do Plantão? 5 Ferramentas Que Funcionam',
      category:'ansiedade',
      readTime:'7 min',
      evidence:'GRADE B',
      excerpt:'A ansiedade pré-plantão é real e tem nome: ansiedade antecipatória. Baseada em estudos de pico de cortisol matinal, aqui estão 5 ferramentas que reduzem o pico de adrenalina antes de entrar no hospital.',
      body:[
        {type:'p', text:'A ansiedade antecipatória acontece quando o cérebro antecipa uma ameaça — o plantão — e dispara cortisol e adrenalina antes mesmo de você bater o ponto. O resultado: coração acelerado, mãos frias, vontade de não sair de casa.'},
        {type:'h2', text:'5 ferramentas baseadas em evidência'},
        {type:'p', text:'1. Grounding 5-4-3-2-1: Nome 5 coisas que você vê, 4 que toca, 3 que ouve, 2 que cheira, 1 que saboreia. Trabalha porque força o córtex pré-frontal a processar dados sensoriais, interrompendo o loop de ansiedade na amígdala.'},
        {type:'p', text:'2. Rotina de chegada: Crie um ritual de 5 minutos ao chegar no hospital. Café, checar escala, revisar medicação. A previsibilidade reduz ansiedade — o cérebro adora padrões.'},
        {type:'p', text:'3. Lista de "o que está no meu controle": Escreva 3 coisas que você controla (sua técnica, sua empatia, sua higiene das mãos) e 3 que não controla (número de pacientes, disposição de leitos, decisões médicas). Foque só nas primeiras.'},
        {type:'p', text:'4. Conversa interna reframe: Troque "tenho que aguentar mais 12 horas" por "vou cuidar de N pacientes hoje, um de cada vez". O cérebro processa "12 horas" como ameaça e "um paciente" como tarefa.'},
        {type:'p', text:'5. Movimento antes do plantão: 5 minutos de caminhada ou alongamento. Exercício leve consome o excesso de adrenalina circulante. Não precisa ser academia — basta caminhar do estacionamento até o posto.'},
        {type:'quote', text:'Ansiedade não é fraqueza. É um cérebro protegendo você demais. O objetivo não é eliminá-la, mas administrá-la.'}
      ],
      references:[
        'APA. Clinical Practice Guideline for the Treatment of Anxiety. 2023.',
        'Clark DA, Beck AT. Cognitive Therapy of Anxiety Disorders. Guilford; 2010.'
      ]
    },
    {
      id:'zen-06',
      title:'Dor nas Costas do Enfermagem: Prevenção e Alívio em 15 Minutos',
      category:'fisico',
      readTime:'10 min',
      evidence:'GRADE A',
      excerpt:'80% dos enfermeiros relatam dor lombar. É a lesão ocupacional mais comum — e a mais evitável. Protocolo de 15 minutos de alongamento e técnica de mobilização baseado em guidelines da AORN.',
      body:[
        {type:'p', text:'Enfermagem é a profissão com maior taxa de lesões musculoesqueléticas da saúde. Mobilizar pacientes, virar camas, permanecer em pé por horas — tudo sobrecarrega a coluna. Mas a dor não é inevitável.'},
        {type:'h2', text:'Os 3 maiores erros mecânicos'},
        {type:'list', items:[
          'Virar paciente sozinho quando há ajuda disponível (overload de L4-L5)',
          'Flexionar a coluna em vez de flexionar os joelhos (discos sofrem 2-3x mais pressão)',
          'Tracionar o paciente com os braços esticados (ombro e lombar absorvem o impacto)'
        ]},
        {type:'h2', text:'Protocolo de 15 minutos (antes ou após o plantão)'},
        {type:'p', text:'1. Gato-Camelo (2 min): Em 4 apoios, alterne entre arquear e relaxar a coluna. 10 repetições lentas. Mobiliza toda a coluna vertebral.'},
        {type:'p', text:'2. Joelho ao peito (2 min): Deitado, leve um joelho de cada vez ao peito. Segure 20 segundos. Alonga lombar e glúteo.'},
        {type:'p', text:'3. Piriforme (3 min): Deitado, cruzo o tornozelo sobre o joelho oposto e puxo a coxa. Segure 30s cada lado. Alivia ciático.'},
        {type:'p', text:'4. Parede e escápulas (3 min): Costas na parede, braços em "W". Deslize braços para cima e para baixo mantendo contato. 15 reps. Reverte a postura curvada.'},
        {type:'p', text:'5. Agachamento isométrico (3 min): Costas na parede, desça até 90°. Segure 30s, 3 séries. Fortalece quadriceps que protege a lombar.'},
        {type:'p', text:'6. Respiração diafragmática (2 min): Deitado, uma mão no peito outra no abdômen. Inspira só com o abdômen. 10 respirações. Libera tensão diafragmática que.reflete na lombar.'},
        {type:'quote', text:'Sua coluna vai durar mais que sua carreira. Trate-a como equipamento de alto valor.'},
        {type:'p', text:'Use equipamentos de mobilização: lençóis deslizantes, levantadores mecânicos, camas com tilt. A Resolução COFEN 550/2017 garante o direito a equipamento ergonômico. Exija.'}
      ],
      references:[
        'AORN. Safe Patient Handling and Movement Guideline. 2024.',
        'Nelson A, et al. Safe Patient Handling and Movement. Am J Nurs. 2003.',
        'COFEN. Resolução 550/2017. Condições de trabalho e saúde do enfermeiro.'
      ]
    },
    {
      id:'zen-07',
      title:'Depressão em Profission de Enfermagem: Rompendo o Silêncio',
      category:'identificacao',
      readTime:'14 min',
      evidence:'GRADE A',
      excerpt:'A prevalência de depressão em enfermeiros é 2x maior que a população geral. Este artigo aborda sinais, diferença entre tristeza e depressão clínica, e como buscar ajuda sem medo de julgamento profissional.',
      body:[
        {type:'p', text:'Dados da OPAS (2023): 28% dos profissionais de enfermagem brasileiros apresentam sintomas depressivos. A taxa sobe para 41% entre os que trabalham em UTI e emergência. Não é coincidência — é ocupacional.'},
        {type:'h2', text:'Tristeza vs. Depressão: a diferença que importa'},
        {type:'p', text:'Tristeza é uma emoção. Tem causa identificável (perda, frustração, cansaço), dura horas a dias e melhora com descanso e apoio social. Depressão é uma condição clínica. Pode não ter causa clara, dura 2+ semanas, e não melhora só com descanso.'},
        {type:'h2', text:'9 sinais que diferenciam depressão de cansaço'},
        {type:'list', items:[
          'Anedonia: nada dá prazer (antes gostava de cozinhar, agora não liga)',
          'Desesperança: "não vai melhorar, nunca vai mudar"',
          'Alteração de peso > 5% em 1 mês (sem dieta)',
          'Insônia OU hipersônia (dorme 12h e acorda cansado)',
          'Lentificação motora ou pensamento arrastado',
          'Sentimento de culpa excessivo ("tudo é minha culpa")',
          'Diminuição da concentração (ler um texto e não absorver)',
          'Ideação: "melhor não estar aqui" (QUALQUER pensamento = procure ajuda)',
          'Irritabilidade em vez de tristeza (comum em homens e profissionais de saúde)'
        ]},
        {type:'p', text:'Profissionais de saúde têm uma barreira única: saber demais. Reconhecem os sintomas em pacientes mas se ignoram. "Eu sei o que é, vai passar" — é o que todo paciente diz. E o que todo enfermeiro também.'},
        {type:'h2', text:'Onde buscar ajuda (sem julgamento)'},
        {type:'list', items:[
          'CAPS — Gratuito, sem necessidade de encaminhamento',
          'Programa de Saúde do Trabalhador do seu hospital',
          'Pelo SUS: agendamento pelo app ConecteSUS ou UBS',
          'Telefones 24h: CVV 188 (gratuito, anônimo)',
          'Samaritanos: 0800 045 5555 (24h)',
          'COFEN/Coren: alguns conselhos oferecem atendimento psicológico gratuito'
        ]},
        {type:'quote', text:'Procurar ajuda psiquiátrica não é falhar como profissional. É o ato mais profissional que você pode fazer.'},
        {type:'p', text:'Tratamento funciona: 80% dos quadros depressivos respondem à terapia cognitivo-comportamental (TCC) associada ou não a medicação. O problema não é falta de tratamento — é a barreira do estigma.'}
      ],
      references:[
        'OPAS/OMS. Salud mental de los trabajadores de la salud. 2023.',
        'APA. Practice Guideline for the Treatment of Depression. 2023.',
        'CVV. Centro de Valorização da Vida. cvv.org.br.'
      ]
    },
    {
      id:'zen-08',
      title:'Nutrição do Plantão: O Que Comer (e o Que Evitar) em 12h',
      category:'fisico',
      readTime:'9 min',
      evidence:'GRADE B',
      excerpt:'O enfermeiro come o que sobra, no tempo que sobra, onde sobra. Este guia prático mostra como planejar alimentação em 12h de plantão para manter energia estável sem picos de cafeína e açúcar.',
      body:[
        {type:'p', text:'A realidade: 67% dos enfermeiros relatam pular refeições durante o plantão e 52% consomem 4+ xícaras de café por turno. O resultado são picos e quedas de glicemia que imitam ansiedade, tremores e confusão mental.'},
        {type:'h2', text:'Protocolo alimentar de 12h'},
        {type:'p', text:'Antes do plantão (30 min antes): Café da manhã real. Ovos (proteína sacia), aveia (energia lenta), fruta (potássio para retenção). Evite: pão branco + café (pico de glicose seguido de crash em 90 min).'},
        {type:'p', text:'Meio da manhã (3-4h de plantão): Snack de proteína. Iogurte natural + granola. Castanhas (6-8 unidades). Barrinha sem açúcar. Evite: bolacha + refrigerante (açúcar rápido = crash em 40 min).'},
        {type:'p', text:'Almoço (6-7h): A refeição mais importante do plantão. Proteína magra (frango/peixe), carboidrato complexo (arroz integral/batata doce), vegetais coloridos (fibras + micronutrientes). Evite: massa branca + molho (inércia digestiva, sonolência).'},
        {type:'p', text:'Meio da tarde (9-10h): Snack leve. Fruta + pasta de amendoim. Hummus + cenoura. Evite: chocolate + energético (ciclo de pico e queda).'},
        {type:'p', text:'Final do plantão: Reidratação. Água + eletrólitos (água de coco). Se sentir fome real: ovo cozido ou queijo. Evite: fast food na saída (inflamação + má qualidade de sono).'},
        {type:'h2', text:'Gerenciamento de cafeína'},
        {type:'p', text:'Regra 90/20: cafeína leva 20 min para fazer efeito e dura ~4-5h. Tome 20 min antes de precisar do pico (não quando já está exausto). Última dose: 6h antes de dormir. Máximo: 400mg/dia (4 xícaras de café expresso).'},
        {type:'quote', text:'Comer bem no plantão não é luxo. É segurança do paciente — um enfermeiro hipoglicêmico é um enfermeiro propenso a erros.'},
        {type:'p', text:'Hidratação: 30-35ml/kg/dia. Para 70kg: ~2,1L. Divida em 4 momentos: 500ml no início, 500ml no meio, 500ml na segunda metade, 500ml no final. Use garrafa marcada — visual ajuda a manter o ritmo.'}
      ],
      references:[
        'WHO. Healthy diet. Fact sheet. 2020.',
        'ANVISA. Guia alimentar para a população brasileira. 2014.',
        'Caffeine: mechanism of action and performance. Eur J Nutr. 2018.'
      ]
    },
    {
      id:'zen-09',
      title:'Luto do Enfermeiro: Como Processar a Perda de Pacientes',
      category:'emocional',
      readTime:'11 min',
      evidence:'GRADE B',
      excerpt:'Enfermeiros enfrentam a morte mais vezes em um mês do que a maioria das pessoas em uma vida. Mas ninguém ensina a lidar com o luto ocupacional. Este artigo aborda luto anticipatório, luto não reconhecido e estratégias de coping.',
      body:[
        {type:'p', text:'O enfermeiro que trabalha em UTI, oncologia ou emergência pode perder 5-10 pacientes por mês. A sociedade reconhece o luto por familiares, mas não reconhece o luto por pacientes. É o "luto não reconhecido" — e é um dos maiores fatores de exaustão emocional na enfermagem.'},
        {type:'h2', text:'Tipos de luto ocupacional'},
        {type:'p', text:'1. Luto antecipatório: Começa antes do óbito. Você sabe que o paciente não vai melhorar. Sentimentos: impotência, tristeza, hipervigilância. É um luto que ninguém valida porque "o paciente ainda está vivo".'},
        {type:'p', text:'2. Luto súbito: Óbito inesperado (PCR, trauma, embolia). O impacto é maior porque não houve preparação emocional. A sensação de "eu deveria ter feito mais" é quase universal.'},
        {type:'p', text:'3. Luto acumulado: Múltiplas perdas em sequência sem tempo de processar. É o que leva ao burnout. Cada perda não processada se acumula como juros emocionais.'},
        {type:'h2', text:'Estratégias de coping baseadas em evidência'},
        {type:'p', text:'1. Validar o luto: Você era o enfermeiro daquela pessoa por 12h. Você cuidou do corpo dela. É normal sentir perda. Não é "fraqueza profissional" — é humanidade.'},
        {type:'p', text:'2. Ritual pessoal: Pequenos rituais ajudam o cérebro a fechar o ciclo. Uma respiração silenciosa após o óbito. Escrever o nome do paciente em um caderno. Acender uma vela. O ritual não precisa ser religioso — precisa ser seu.'},
        {type:'p', text:'3. Debriefing: Após um óbito difícil, reúna a equipe por 10 minutos. Não para revisar o caso clinicamente — para processar emocionalmente. "Como você está?" é a pergunta mais terapêutica que um colega pode fazer.'},
        {type:'p', text:'4. Separação trabalho-vida: Crie uma transição física entre o hospital e a casa. Trocar de roupa, lavar as mãos intencionalmente (não só por higiene — como ritual de "lavar o dia"), ouvir música específica no trajeto.'},
        {type:'p', text:'5. Buscar ajuda se: sonhos recorrentes com o paciente, evitar o leito onde o óbito ocorreu, pensamentos de "não devia ter sido enfermeiro", ou se 2 semanas se passaram e a tristeza não diminuiu.'},
        {type:'quote', text:'Você não perdeu um paciente. Você perdeu uma pessoa que confiou em você no momento mais vulnerável dela. Isso é sagrado — e dói porque é sagrado.'},
        {type:'p', text:'Luto ocupacional não é diagnóstico. É uma resposta humana normal a uma perda real. O problema não é sentir — é não ter espaço para sentir.'}
      ],
      references:[
        'PMC. Grief and loss in ICU nurses. Intensive Crit Care Nurs. 2022.',
        'Worden JW. Grief Counseling and Grief Therapy. 5th ed. Springer; 2018.',
        'COFEN. Saúde mental do profissional de enfermagem. 2023.'
      ]
    },
    {
      id:'zen-10',
      title:'Construindo Resiliência: Não é Apanhar Tudo, é Saber Soltar',
      category:'resiliencia',
      readTime:'13 min',
      evidence:'GRADE A',
      excerpt:'Resiliência não é aguentar calado. É a capacidade de absorver impacto, processar e voltar — adaptado, não endurecido. Baseado no modelo de resiliência ocupacional de Southwick & Charney (2018).',
      body:[
        {type:'p', text:'O maior mito sobre resiliência na enfermagem: "resiliente é quem não chora, não reclama, aguenta tudo". Falso. Resiliência é o oposto disso. O modelo científico (Southwick & Charney, 2018) define resiliência como a capacidade de adaptar-se e crescer frente à adversidade — não de suportar sem reagir.'},
        {type:'h2', text:'Os 7 pilares da resiliência ocupacional'},
        {type:'p', text:'1. Otimismo realista: Não é "vai dar tudo certo". É "mesmo se der errado, eu tenho ferramentas para lidar". Estudo de Seligman mostra que otimistas têm 35% menos burnout — não porque ignoram problemas, mas porque focam em soluções.'},
        {type:'p', text:'2. Aceitação do que não controla: Você não controla o número de pacientes, a gravidade dos casos, as decisões médicas. Você controla sua técnica, sua empatia, sua higiene das mãos. Foco no que controla = menos ansiedade.'},
        {type:'p', text:'3. Rede de apoio ativa: Ter 1-2 pessoas com quem você pode falar abertamente sobre o trabalho reduz burnout em 40%. Não precisa ser terapeuta — pode ser colega, parceiro, amigo. O que importa é a autenticidade da conversa.'},
        {type:'p', text:'4. Modelagem de papéis: Identifique um enfermeiro sênior que você admira. Observe como lida com estresse. Pergunte: "Como você faz isso há 20 anos sem surtar?" A resposta pode surpreender — e ensinar.'},
        {type:'p', text:'5. Significado: Conecte-se ao porquê. Você escolheu enfermagem por uma razão. Revisitá-la regularmente (não só quando está mal) protege contra o cinismo do burnout. Escreva o porquê no crachá ou no armário.'},
        {type:'p', text:'6. Cuidado físico como ativo: Sono, alimentação, movimento. Não é "saúde" no sentido abstrato — é a base neuroquímica da resiliência. Um cérebro dormindo 5h não consegue ser resiliente, por mais que a vontade exista.'},
        {type:'p', text:'7. Humor: Não é piada com paciente. É o humor interno que permite rir de situações absurdas com um colega. O humor reduz cortisol e aumenta oxitocina. É uma ferramenta de sobrevivência — não frivolidade.'},
        {type:'h2', text:'Resiliência vs. Endurecimento'},
        {type:'p', text:'Resiliência: Sente a dor, processa, adapta-se, volta com novas ferramentas. Cresce. Endurecimento: Suprime a dor, ignora, endurece, fica cínico. Não cresce — acumula. O endurecido parece forte, mas está quebrando por dentro.'},
        {type:'quote', text:'A resiliência não é uma armadura. É uma árvore que dobra no vento mas não quebra — porque tem raízes.'},
        {type:'p', text:'Construa resiliência como treino muscular: pequenos desafios diários (respiração, reflexão, conversa honesta) que, ao longo de meses, criam a capacidade de absorver grandes impactos sem quebrar. Não é dom. É prática.'}
      ],
      references:[
        'Southwick SM, Charney DS. Resilience: The Science of Mastering Life\'s Greatest Challenges. Cambridge; 2018.',
        'Seligman MEP. Flourish. Free Press; 2011.',
        'Menezes VD, et al. Resilience of nursing professionals. Rev Bras Enferm. 2021.'
      ]
    }
  ],

  // ═════════════════════════════════════════════════════════════════
  // ÁUDIOS GUIADOS (referências + players simulados)
  // ═════════════════════════════════════════════════════════════════
  audios: [
    { id:'aud-01', title:'Respiração Diafragmática — 5 min', desc:'Áudio guiado para relaxamento rápido entre atendimentos.', duration:'5:00', category:'respiracao', icon:'fa-wind' },
    { id:'aud-02', title:'Body Scan Completo — 15 min', desc:'Relaxamento muscular progressivo, ideal após o plantão.', duration:'15:00', category:'relaxamento', icon:'fa-spa' },
    { id:'aud-03', title:'Meditação para Dormir — 10 min', desc:'Técnica específica para dormir pós-plantão noturno.', duration:'10:00', category:'sono', icon:'fa-moon' },
    { id:'aud-04', title:'Grounding 5-4-3-2-1 — 3 min', desc:'Técnica de ancoragem para momentos de ansiedade aguda.', duration:'3:00', category:'ansiedade', icon:'fa-anchor' },
    { id:'aud-05', title:'Compassion Fatigue Reset — 12 min', desc:'Meditação de autocompaixão para profissionais de saúde.', duration:'12:00', category:'emocional', icon:'fa-heart' },
    { id:'aud-06', title:'Micro-pausa de 90 Segundos', desc:'Para usar entre pacientes. Alinha respiração e intenção.', duration:'1:30', category:'respiracao', icon:'fa-stopwatch' }
  ],

  // ═════════════════════════════════════════════════════════════════
  // EXERCÍCIOS INTERATIVOS
  // ═════════════════════════════════════════════════════════════════
  exercises: [
    {
      id:'ex-01',
      title:'Box Breathing 4-4-4-4',
      desc:'Técnica usada por Navy SEALs para controlar estresse em combate. 4 ciclos guiados.',
      duration:'2 min',
      type:'breathing',
      steps:[
        { phase:'Inspira', seconds:4, desc:'Inspire pelo nariz contando até 4' },
        { phase:'Segura', seconds:4, desc:'Mantenha o ar nos pulmões contando até 4' },
        { phase:'Expira', seconds:4, desc:'Solte o ar pela boca contando até 4' },
        { phase:'Pausa', seconds:4, desc:'Permaneça sem ar contando até 4' }
      ]
    },
    {
      id:'ex-02',
      title:'Relaxamento Muscular Progressivo (PMR)',
      desc:'Tensa e relaxe cada grupo muscular. Ideal para dores de plantão.',
      duration:'8 min',
      type:'pmr',
      steps:[
        { phase:'Mãos', seconds:10, desc:'Cerre os punhos com força. Solte.' },
        { phase:'Braços', seconds:10, desc:'Flexione os bíceps. Solte.' },
        { phase:'Ombros', seconds:10, desc:'Eleve os ombros às orelhas. Solte.' },
        { phase:'Rosto', seconds:10, desc:'Aperte olhos e boca. Solte.' },
        { phase:'Peito', seconds:10, desc:'Inspire fundo e segure. Solte.' },
        { phase:'Abdômen', seconds:10, desc:'Contraia o abdômen. Solte.' },
        { phase:'Pernas', seconds:10, desc:'Estique as pernas. Solte.' },
        { phase:'Pés', seconds:10, desc:'Flexe os pés para cima. Solte.' }
      ]
    }
  ],

  // ═════════════════════════════════════════════════════════════════
  // RECURSOS DE APOIO (telefones, links, serviços)
  // ═════════════════════════════════════════════════════════════════
  resources: [
    { name:'CVV — Centro de Valorização da Vida', phone:'188', desc:'Apoio emocional gratuito 24h. Anônimo.', url:'cvv.org.br', icon:'fa-phone', urgent:true },
    { name:'Samaritanos', phone:'0800 045 5555', desc:'Apoio emocional 24h. Gratuito.', url:'samaritanos.org.br', icon:'fa-phone', urgent:true },
    { name:'CAPS', phone:'', desc:'Centro de Atenção Psicossocial — gratuito, sem encaminhamento.', url:'gov.br/saude', icon:'fa-hospital', urgent:false },
    { name:'Programa de Saúde do Trabalhador', phone:'', desc:'Verifique no RH do seu hospital. Você tem direito.', url:'', icon:'fa-briefcase-medical', urgent:false },
    { name:'App: Insight Timer', phone:'', desc:'Meditações gratuitas guiadas. Sem anúncios.', url:'insighttimer.com', icon:'fa-mobile-screen', urgent:false },
    { name:'App: Healthy Minds', phone:'', desc:'Programa gratuito de mindfulness baseado em ciência.', url:'healthyminds.org', icon:'fa-mobile-screen', urgent:false }
  ],

  // ═════════════════════════════════════════════════════════════════
  // FRASES DE APOIO (rotação aleatória)
  // ═════════════════════════════════════════════════════════════════
  affirmations: [
    'O cuidado que você dá hoje matters. Mesmo quando ninguém agradece.',
    'Você não precisa ser perfeita. Precisa estar presente.',
    'Respirar é um ato político num sistema que quer você exausto.',
    'Seu descanso é segurança do paciente. Não é egoísmo.',
    'Você escolheu a profissão que cuida de pessoas. Inclua-se nessa lista.',
    'O paciente de hoje vai esquecer a técnica. Vai lembrar da sua humanidade.',
    'Não é sua responsabilidade salvar todo mundo. É sua responsabilidade fazer o seu melhor hoje.',
    'Um plantão de cada vez. Um paciente de cada vez. Uma respiração de cada vez.'
  ]
};