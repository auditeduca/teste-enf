/* =====================================================================
   Grafo de Conhecimento Clínico — Calculadoras de Enfermagem
   D3.js force-directed graph with NANDA/NIC/NOC/concept/drug nodes
   ===================================================================== */
(function(){
  'use strict';

  // === Dados do grafo (subset representativo dos 52K+ registros) ===
  const graphData = {
    nodes: [
      // NANDA-I
      {id:"NANDA_00046",label:"Hipoglicemia",type:"nanda",code:"00046",domain:"Segurança/Proteção",evidence:"B"},
      {id:"NANDA_00079",label:"Débito cardíaco diminuído",type:"nanda",code:"00079",domain:"Atividade/Repouso",evidence:"A"},
      {id:"NANDA_00032",label:"Risco de lesão",type:"nanda",code:"00032",domain:"Segurança/Proteção",evidence:"B"},
      {id:"NANDA_00204",label:"Perfusão tissular cerebral ineficaz",type:"nanda",code:"00204",domain:"Atividade/Repouso",evidence:"B"},
      {id:"NANDA_00004",label:"Risco de infecção",type:"nanda",code:"00004",domain:"Segurança/Proteção",evidence:"A"},
      {id:"NANDA_00100",label:"Apega materno prejudicado",type:"nanda",code:"00100",domain:"Papel/Relacionamento",evidence:"C"},
      {id:"NANDA_00040",label:"Risco de aspiração",type:"nanda",code:"00040",domain:"Segurança/Proteção",evidence:"B"},
      {id:"NANDA_00088",label:"Lesão por pressão",type:"nanda",code:"00088",domain:"Segurança/Proteção",evidence:"A"},
      {id:"NANDA_00106",label:"Amamentação ineficaz",type:"nanda",code:"00106",domain:"Crescimento/Desenvolvimento",evidence:"B"},
      {id:"NANDA_00005",label:"Risco de desequilíbrio de volume",type:"nanda",code:"00005",domain:"Nutrição",evidence:"B"},
      {id:"NANDA_00023",label:"Toxicidade por medicamento",type:"nanda",code:"00023",domain:"Segurança/Proteção",evidence:"A"},
      {id:"NANDA_00126",label:"Risco de constipação",type:"nanda",code:"00126",domain:"Eliminação",evidence:"C"},

      // NIC
      {id:"NIC_2500",label:"Manejo do débito cardíaco",type:"nic",code:"2500",domain:"Sistema circulatório",evidence:"A"},
      {id:"NIC_2300",label:"Administração de medicação",type:"nic",code:"2300",domain:"Sistema farmacológico",evidence:"A"},
      {id:"NIC_2304",label:"Administração de medicação: IV",type:"nic",code:"2304",domain:"Sistema farmacológico",evidence:"A"},
      {id:"NIC_6486",label:"Manejo ambiental: Segurança",type:"nic",code:"6486",domain:"Segurança",evidence:"B"},
      {id:"NIC_6540",label:"Prevenção de úlceras por pressão",type:"nic",code:"6540",domain:"Sistema tegumentar",evidence:"A"},
      {id:"NIC_1050",label:"Amamentação",type:"nic",code:"1050",domain:"Crescimento/Desenvolvimento",evidence:"B"},
      {id:"NIC_4120",label:"Manejo de hipoglicemia",type:"nic",code:"4120",domain:"Sistema endócrino",evidence:"A"},
      {id:"NIC_3200",label:"Precaução contra aspiração",type:"nic",code:"3200",domain:"Segurança",evidence:"B"},
      {id:"NIC_4030",label:"Administração de hemoderivados",type:"nic",code:"4030",domain:"Sistema circulatório",evidence:"A"},
      {id:"NIC_6650",label:"Vigilância: Pós-parto",type:"nic",code:"6650",domain:"Reprodução",evidence:"B"},

      // NOC
      {id:"NOC_0413",label:"Gravidade da hipoglicemia",type:"noc",code:"0413",domain:"Fisiológico: Metabólico",evidence:"A"},
      {id:"NOC_0411",label:"Gravidade da perda sanguínea",type:"noc",code:"0411",domain:"Fisiológico: Sangue",evidence:"A"},
      {id:"NOC_0415",label:"Gravidade da lesão por pressão",type:"noc",code:"0415",domain:"Fisiológico: Tegumentar",evidence:"A"},
      {id:"NOC_1002",label:"Taxa de amamentação: estabelecida",type:"noc",code:"1002",domain:"Crescimento/Desenvolvimento",evidence:"B"},
      {id:"NOC_0703",label:"Gravidade da infecção",type:"noc",code:"0703",domain:"Fisiológico: Imunológico",evidence:"A"},
      {id:"NOC_1902",label:"Risco de lesão: recém-nascido",type:"noc",code:"1902",domain:"Segurança",evidence:"B"},
      {id:"NOC_0419",label:"Gravidade do débito cardíaco",type:"noc",code:"0419",domain:"Fisiológico: Cardíaco",evidence:"A"},

      // Conceitos
      {id:"CONCEPT_CLIN_CARDIO",label:"Cardiologia",type:"concept",code:"CLIN.CARDIO",snomed:"867868471"},
      {id:"CONCEPT_CLIN_ENDOCRINO",label:"Endocrinologia",type:"concept",code:"CLIN.ENDOCRINO",snomed:"281020001"},
      {id:"CONCEPT_CLIN_NEONATO",label:"Neonatologia",type:"concept",code:"CLIN.NEONATO",snomed:"40880004"},
      {id:"CONCEPT_CLIN_INFECCAO",label:"Controle de Infecção",type:"concept",code:"CLIN.INFECT",snomed:"409822000"},

      // Medicamentos
      {id:"DRUG_INSULIN",label:"Insulina",type:"drug",code:"ATC_A10AB01",high_alert:true},
      {id:"DRUG_NOREPI",label:"Noradrenalina",type:"drug",code:"ATC_C01CA03",high_alert:true},
      {id:"DRUG_HEPARIN",label:"Heparina",type:"drug",code:"ATC_B01AB01",high_alert:true},
      {id:"DRUG_EPHEDRINE",label:"Epinefrina",type:"drug",code:"ATC_C01CA24",high_alert:true},
    ],
    links: [
      // NANDA → NIC (therapeutic)
      {source:"NANDA_00046",target:"NIC_4120",type:"therapeutic",weight:0.95,evidence:"A"},
      {source:"NANDA_00079",target:"NIC_2500",type:"therapeutic",weight:0.92,evidence:"A"},
      {source:"NANDA_00032",target:"NIC_6486",type:"therapeutic",weight:0.80,evidence:"B"},
      {source:"NANDA_00204",target:"NIC_2500",type:"therapeutic",weight:0.85,evidence:"B"},
      {source:"NANDA_00004",target:"NIC_6486",type:"therapeutic",weight:0.88,evidence:"A"},
      {source:"NANDA_00088",target:"NIC_6540",type:"therapeutic",weight:0.93,evidence:"A"},
      {source:"NANDA_00106",target:"NIC_1050",type:"therapeutic",weight:0.90,evidence:"B"},
      {source:"NANDA_00040",target:"NIC_3200",type:"therapeutic",weight:0.85,evidence:"B"},
      {source:"NANDA_00023",target:"NIC_2300",type:"causal",weight:0.78,evidence:"A"},

      // NIC → NOC (outcome)
      {source:"NIC_4120",target:"NOC_0413",type:"outcome",weight:0.91,evidence:"A"},
      {source:"NIC_2500",target:"NOC_0419",type:"outcome",weight:0.89,evidence:"A"},
      {source:"NIC_6540",target:"NOC_0415",type:"outcome",weight:0.92,evidence:"A"},
      {source:"NIC_1050",target:"NOC_1002",type:"outcome",weight:0.87,evidence:"B"},
      {source:"NIC_6486",target:"NOC_0703",type:"outcome",weight:0.75,evidence:"B"},
      {source:"NIC_6486",target:"NOC_1902",type:"outcome",weight:0.82,evidence:"B"},

      // NANDA → NOC (assessment)
      {source:"NANDA_00046",target:"NOC_0413",type:"assessment",weight:0.90,evidence:"A"},
      {source:"NANDA_00079",target:"NOC_0419",type:"assessment",weight:0.88,evidence:"A"},
      {source:"NANDA_00088",target:"NOC_0415",type:"assessment",weight:0.93,evidence:"A"},

      // Conceito → NANDA (categorizes)
      {source:"CONCEPT_CLIN_ENDOCRINO",target:"NANDA_00046",type:"categorizes",weight:0.70,evidence:"B"},
      {source:"CONCEPT_CLIN_CARDIO",target:"NANDA_00079",type:"categorizes",weight:0.72,evidence:"B"},
      {source:"CONCEPT_CLIN_CARDIO",target:"NANDA_00204",type:"categorizes",weight:0.68,evidence:"B"},
      {source:"CONCEPT_CLIN_NEONATO",target:"NANDA_00106",type:"categorizes",weight:0.65,evidence:"C"},
      {source:"CONCEPT_CLIN_INFECCAO",target:"NANDA_00004",type:"categorizes",weight:0.75,evidence:"A"},

      // Drug → NIC (administers)
      {source:"DRUG_INSULIN",target:"NIC_2304",type:"administers",weight:0.95,evidence:"A"},
      {source:"DRUG_NOREPI",target:"NIC_2500",type:"administers",weight:0.90,evidence:"A"},
      {source:"DRUG_HEPARIN",target:"NIC_2304",type:"administers",weight:0.88,evidence:"A"},
      {source:"DRUG_EPHEDRINE",target:"NIC_4120",type:"administers",weight:0.82,evidence:"B"},

      // Drug → NANDA (treats)
      {source:"DRUG_INSULIN",target:"NANDA_00046",type:"treats",weight:0.85,evidence:"A"},
      {source:"DRUG_NOREPI",target:"NANDA_00079",type:"treats",weight:0.80,evidence:"A"},
    ]
  };

  // === Cores por tipo ===
  const typeColors = {
    nanda:   '#2563eb',
    nic:     '#1a3e74',
    noc:     '#3b82f6',
    concept: '#5b6b7f',
    drug:    '#081527',
  };
  const typeLabels = {
    nanda:'NANDA-I', nic:'NIC', noc:'NOC', concept:'Conceito', drug:'Medicamento'
  };
  const relLabels = {
    therapeutic:'Terapêutica', causal:'Causal', outcome:'Desfecho',
    assessment:'Avaliação', categorizes:'Categoriza', administers:'Administra',
    treats:'Trata'
  };

  // === State ===
  let currentFilter = 'all';
  let svg, g, simulation, linkSel, nodeSel, labelSel;
  let zoomBehavior;
  let selectedNode = null;

  // === Init ===
  function init(){
    const container = document.getElementById('graph-canvas');
    if(!container) return;
    const width = container.clientWidth;
    const height = container.clientHeight;

    svg = d3.select('#graph-canvas').append('svg')
      .attr('width', width).attr('height', height)
      .attr('viewBox', [0, 0, width, height])
      .style('position','absolute').style('top','0').style('left','0');

    // Gradient defs
    const defs = svg.append('defs');
    defs.append('marker')
      .attr('id','arrowhead').attr('viewBox','0 -5 10 10')
      .attr('refX',20).attr('refY',0).attr('markerWidth',6).attr('markerHeight',6)
      .attr('orient','auto')
      .append('path').attr('d','M0,-5L10,0L0,5').attr('fill','#94a3b8');

    g = svg.append('g');

    zoomBehavior = d3.zoom().scaleExtent([0.3, 4]).on('zoom', (e) => {
      g.attr('transform', e.transform);
    });
    svg.call(zoomBehavior);

    // Stats
    document.getElementById('stat-nodes').textContent = graphData.nodes.length;
    document.getElementById('stat-edges').textContent = graphData.links.length;

    renderGraph('all');
    bindControls();
  }

  function renderGraph(filter){
    currentFilter = filter;
    const filteredNodes = filter === 'all'
      ? graphData.nodes
      : graphData.nodes.filter(n => n.type === filter);
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredLinks = graphData.links.filter(l => nodeIds.has(l.source) || nodeIds.has(l.target));
    // Normalize link source/target
    const links = filteredLinks.map(l => ({
      ...l,
      source: l.source,
      target: l.target
    }));

    g.selectAll('*').remove();

    simulation = d3.forceSimulation(filteredNodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(d => 80 + (1 - d.weight) * 60).strength(0.3))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(svg.attr('viewBox').baseVal.width / 2, svg.attr('viewBox').baseVal.height / 2))
      .force('collision', d3.forceCollide().radius(d => nodeRadius(d) + 8));

    linkSel = g.append('g').attr('class','links')
      .selectAll('line').data(links).enter().append('line')
      .attr('stroke','#cbd5e1').attr('stroke-width', d => 1 + d.weight * 2.5)
      .attr('stroke-opacity', 0.6).attr('marker-end','url(#arrowhead)');

    nodeSel = g.append('g').attr('class','nodes')
      .selectAll('circle').data(filteredNodes).enter().append('circle')
      .attr('r', d => nodeRadius(d))
      .attr('fill', d => typeColors[d.type] || '#5b6b7f')
      .attr('stroke','#fff').attr('stroke-width', 2)
      .style('cursor','pointer')
      .on('click', (e, d) => { e.stopPropagation(); selectNode(d); })
      .on('mouseenter', (e, d) => { e.target.style.stroke = '#2563eb'; e.target.style.strokeWidth = 3; })
      .on('mouseleave', (e, d) => { e.target.style.stroke = '#fff'; e.target.style.strokeWidth = 2; })
      .call(d3.drag()
        .on('start', (e, d) => { if(!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
        .on('end', (e, d) => { if(!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
      );

    labelSel = g.append('g').attr('class','labels')
      .selectAll('text').data(filteredNodes).enter().append('text')
      .text(d => d.label.length > 22 ? d.label.substring(0,20) + '…' : d.label)
      .attr('font-size','11px').attr('font-family','Manrope, sans-serif')
      .attr('fill','#1a3e74').attr('font-weight','600')
      .attr('text-anchor','middle').attr('dy', d => nodeRadius(d) + 14)
      .style('pointer-events','none').style('user-select','none');

    simulation.on('tick', () => {
      linkSel
        .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      nodeSel.attr('cx', d => d.x).attr('cy', d => d.y);
      labelSel.attr('x', d => d.x).attr('y', d => d.y);
    });
  }

  function nodeRadius(d){
    const sizes = { nanda: 12, nic: 10, noc: 9, concept: 14, drug: 11 };
    return sizes[d.type] || 9;
  }

  function selectNode(d){
    selectedNode = d;
    const detail = document.getElementById('node-detail');
    const relPanel = document.getElementById('relations-panel');
    const relList = document.getElementById('relations-list');

    let metaRows = '';
    if(d.code) metaRows += `<div class="node-meta-row"><span class="k">Código</span><span class="v">${d.code}</span></div>`;
    if(d.domain) metaRows += `<div class="node-meta-row"><span class="k">Domínio</span><span class="v">${d.domain}</span></div>`;
    if(d.evidence) metaRows += `<div class="node-meta-row"><span class="k">Evidência GRADE</span><span class="v">${d.evidence}</span></div>`;
    if(d.snomed) metaRows += `<div class="node-meta-row"><span class="k">SNOMED CT</span><span class="v">${d.snomed}</span></div>`;
    if(d.high_alert) metaRows += `<div class="node-meta-row"><span class="k">High Alert</span><span class="v">Sim</span></div>`;
    metaRows += `<div class="node-meta-row"><span class="k">Tipo</span><span class="v">${typeLabels[d.type] || d.type}</span></div>`;

    detail.innerHTML = `
      <h3>${d.label}</h3>
      <div class="node-code">${d.id}</div>
      <div class="node-meta">${metaRows}</div>
    `;

    // Find relations
    const rels = graphData.links.filter(l => l.source === d.id || l.target === d.id || (l.source.id === d.id) || (l.target.id === d.id));
    if(rels.length > 0){
      relPanel.style.display = 'block';
      relList.innerHTML = rels.map(r => {
        const fromId = typeof r.source === 'object' ? r.source.id : r.source;
        const toId = typeof r.target === 'object' ? r.target.id : r.target;
        const fromNode = graphData.nodes.find(n => n.id === fromId);
        const toNode = graphData.nodes.find(n => n.id === toId);
        const direction = fromId === d.id ? '→' : '←';
        const otherNode = fromId === d.id ? toNode : fromNode;
        return `<div class="graph-relation-item">
          <span>${d.label}</span>
          <span class="rel-arrow">${direction}</span>
          <span>${otherNode ? otherNode.label : toId}</span>
          <span class="rel-type">${relLabels[r.type] || r.type}</span>
          <span class="rel-weight">peso: ${r.weight.toFixed(2)} · ev: ${r.evidence}</span>
        </div>`;
      }).join('');
    } else {
      relPanel.style.display = 'none';
    }
  }

  function bindControls(){
    // Filter buttons
    document.querySelectorAll('.graph-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.graph-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderGraph(btn.dataset.filter);
      });
    });

    // Zoom controls
    document.getElementById('btn-zoom-in')?.addEventListener('click', () => {
      svg.transition().duration(300).call(zoomBehavior.scaleBy, 1.3);
    });
    document.getElementById('btn-zoom-out')?.addEventListener('click', () => {
      svg.transition().duration(300).call(zoomBehavior.scaleBy, 0.7);
    });
    document.getElementById('btn-reset')?.addEventListener('click', () => {
      svg.transition().duration(500).call(zoomBehavior.transform, d3.zoomIdentity);
    });
    document.getElementById('btn-fullscreen')?.addEventListener('click', () => {
      const el = document.getElementById('graph-canvas');
      if(!document.fullscreenElement) el.requestFullscreen?.(); else document.exitFullscreen?.();
    });

    // Search
    const searchInput = document.getElementById('graph-search-input');
    searchInput?.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      if(!q) {
        nodeSel.attr('opacity', 1); labelSel.attr('opacity', 1); linkSel.attr('opacity', 0.6);
        return;
      }
      nodeSel.attr('opacity', d => d.label.toLowerCase().includes(q) || d.id.toLowerCase().includes(q) || (d.code && d.code.includes(q)) ? 1 : 0.15);
      labelSel.attr('opacity', d => d.label.toLowerCase().includes(q) || d.id.toLowerCase().includes(q) ? 1 : 0.1);
    });
  }

  // Init on DOM ready
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
