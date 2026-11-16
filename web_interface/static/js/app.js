/* Assistente de Atividades v2 - JavaScript unico, sem bibliotecas externas.
   Regra de seguranca: todo texto vindo do usuario ou do bot entra na pagina
   por textContent (nunca innerHTML), para nao executar codigo digitado no chat. */
(function () {
  'use strict';
  var pagina = document.body.dataset.pagina;
  var LIMIAR_FALLBACK = 0.5;   // mesmo valor do FallbackClassifier em rasa/config.yml

  // ---------- utilidades ----------
  function el(tag, classe, texto) {
    var no = document.createElement(tag);
    if (classe) no.className = classe;
    if (texto !== undefined && texto !== null) no.textContent = String(texto);
    return no;
  }
  function limpar(no) { while (no.firstChild) no.removeChild(no.firstChild); return no; }
  function pct(v) { return Math.round((v || 0) * 100) + '%'; }
  function api(url, corpo) {
    var opcoes = corpo === undefined ? {} : {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(corpo)
    };
    return fetch(url, opcoes).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok) { var e = new Error(j.erro || ('HTTP ' + r.status)); e.dados = j; throw e; }
        return j;
      });
    });
  }

  // ---------- apelido (identifica a conversa e o dono dos registros) ----------
  var apelido = 'visitante';
  try { apelido = localStorage.getItem('apelido') || ''; } catch (e) { apelido = ''; }
  function definirApelido(novo) {
    apelido = (novo || '').replace(/[^A-Za-z0-9_-]/g, '').slice(0, 24) || 'visitante';
    try { localStorage.setItem('apelido', apelido); } catch (e) { /* navegador sem armazenamento */ }
    document.getElementById('apelido-atual').textContent = apelido;
  }
  if (!apelido) apelido = 'aluno' + Math.floor(100 + Math.random() * 900);
  definirApelido(apelido);
  document.getElementById('apelido-botao').addEventListener('click', function () {
    var novo = window.prompt('Seu apelido (letras e números, sem espaço). Evite nome completo.', apelido);
    if (novo !== null) { definirApelido(novo); window.location.reload(); }
  });

  // ---------- barras de confianca (usadas no Raio-X e no Duelo) ----------
  function barras(ranking, vencedor, comLimiar) {
    var caixa = el('div');
    (ranking || []).forEach(function (r) {
      var linha = el('div', 'barra-linha' + (r.nome === vencedor ? ' vencedora' : ''));
      linha.appendChild(el('span', 'nome', r.nome));
      var trilho = el('div', 'trilho'); var cheio = el('i');
      trilho.appendChild(cheio);
      if (comLimiar) { var lim = el('span', 'limiar'); lim.style.left = (LIMIAR_FALLBACK * 100) + '%'; lim.title = 'limiar de fallback'; trilho.appendChild(lim); }
      linha.appendChild(trilho);
      linha.appendChild(el('span', 'pct', pct(r.confianca)));
      caixa.appendChild(linha);
      setTimeout(function () { cheio.style.width = Math.max(1, (r.confianca || 0) * 100) + '%'; }, 60);
    });
    return caixa;
  }

  // =====================================================================
  // CHAT + RAIO-X (tambem usado pela tela de Replay)
  // =====================================================================
  function iniciarChat() {
    var modo = document.body.dataset.modo;
    var mensagens = document.getElementById('mensagens');
    var estacoes = document.getElementById('estacoes');
    var vazio = document.getElementById('raiox-vazio');
    var passo = document.getElementById('passo-a-passo');
    var botaoEtapa = document.getElementById('proxima-etapa');
    var filaEtapas = [];

    function balao(classe, texto, meta) {
      var b = el('div', 'balao ' + classe, texto);
      if (meta) b.appendChild(el('span', 'meta', meta));
      mensagens.appendChild(b);
      mensagens.scrollTop = mensagens.scrollHeight;
      return b;
    }

    function linhaQuebrou(turno) {
      var linha = el('div', 'quebrou');
      if (turno.motivo_auto) linha.appendChild(el('span', 'selo', 'no mural: ' + turno.motivo_auto));
      if (modo !== 'replay') {
        var botao = el('button', null, '🔨 quebrou? reportar');
        botao.type = 'button';
        botao.addEventListener('click', function () {
          var campo = el('input'); campo.placeholder = 'O que estava errado? (opcional) — Enter envia';
          campo.maxLength = 300;
          linha.replaceChild(campo, botao); campo.focus();
          campo.addEventListener('keydown', function (ev) {
            if (ev.key !== 'Enter') return;
            api('/api/quebra', { id: turno.id, comentario: campo.value }).then(function () {
              linha.replaceChild(el('span', 'selo', 'reportado no mural'), campo);
            }).catch(function (e) { linha.replaceChild(el('span', 'selo', 'falhou: ' + e.message), campo); });
          });
        });
        linha.appendChild(botao);
      }
      mensagens.appendChild(linha);
      mensagens.scrollTop = mensagens.scrollHeight;
    }

    // ----- monta as seis estacoes do Raio-X a partir dos dados REAIS do tracker -----
    function preencherRaioX(turno) {
      var x = turno.raiox || {};
      limpar(document.getElementById('x-mensagem')).appendChild(el('span', 'frase-crua', x.texto));

      var tokens = limpar(document.getElementById('x-tokens'));
      (x.tokens || []).forEach(function (t) { tokens.appendChild(el('span', 'ficha', t)); });
      if (!(x.tokens || []).length) tokens.appendChild(el('span', 'nota', 'o Rasa não devolveu os tokens desta mensagem'));

      var intent = limpar(document.getElementById('x-intent'));
      var nome = (x.intent || {}).nome;
      intent.appendChild(barras(x.ranking, nome, true));
      intent.appendChild(el('p', 'nota', nome === 'nlu_fallback'
        ? 'Nenhuma intenção passou do limiar de ' + pct(LIMIAR_FALLBACK) + ' (linha vermelha): o FallbackClassifier assumiu.'
        : 'Vencedora: ' + nome + ' com ' + pct((x.intent || {}).confianca) + '. A linha vermelha é o limiar de fallback (' + pct(LIMIAR_FALLBACK) + ').'));

      var ent = limpar(document.getElementById('x-entidades'));
      var lista = (x.entidades || []).filter(function (e) { return typeof e.inicio === 'number'; })
        .sort(function (a, b) { return a.inicio - b.inicio; });
      if (!lista.length) {
        ent.appendChild(el('p', 'nota', 'Nenhuma entidade extraída desta frase.'));
      } else {
        var frase = el('div', 'frase-marcada'); var cursor = 0; var texto = x.texto || '';
        lista.forEach(function (e) {
          if (e.inicio < cursor) return;
          frase.appendChild(document.createTextNode(texto.slice(cursor, e.inicio)));
          var marca = el('mark', null, texto.slice(e.inicio, e.fim));
          marca.appendChild(el('sub', null, e.entidade));
          frase.appendChild(marca); cursor = e.fim;
        });
        frase.appendChild(document.createTextNode(texto.slice(cursor)));
        ent.appendChild(frase);
        var tab = el('table', 'tabelinha'); var cab = el('tr');
        ['entidade', 'trecho da frase', 'valor entregue pelo NLU'].forEach(function (c) { cab.appendChild(el('th', null, c)); });
        tab.appendChild(cab);
        lista.forEach(function (e) {
          var tr = el('tr');
          tr.appendChild(el('td', 'mono', e.entidade));
          tr.appendChild(el('td', 'mono', texto.slice(e.inicio, e.fim)));
          tr.appendChild(el('td', 'mono', e.valor));
          tab.appendChild(tr);
        });
        ent.appendChild(tab);
      }

      var dec = limpar(document.getElementById('x-decisao'));
      var tabA = el('table', 'tabelinha'); var cabA = el('tr');
      ['ação executada', 'quem decidiu', 'confiança'].forEach(function (c) { cabA.appendChild(el('th', null, c)); });
      tabA.appendChild(cabA);
      (x.acoes || []).forEach(function (a) {
        var tr = el('tr');
        tr.appendChild(el('td', 'mono', a.nome + (a.nome === 'action_listen' ? '  (esperar o usuário)' : '')));
        var td = el('td');
        if (a.politica) td.appendChild(el('span', 'pol' + (a.politica === 'RulePolicy' ? ' regra' : ''), a.politica));
        else td.appendChild(el('span', 'nota', 'encadeada pela ação anterior'));
        tr.appendChild(td);
        tr.appendChild(el('td', null, a.confianca === null || a.confianca === undefined ? '—' : pct(a.confianca)));
        tabA.appendChild(tr);
      });
      dec.appendChild(tabA);
      if ((x.slots_alterados || []).length) {
        var s = el('p', 'nota', 'Slots alterados nesta rodada: ');
        x.slots_alterados.forEach(function (sl) {
          s.appendChild(el('span', 'ficha', sl.nome + ' = ' + (sl.valor === null ? 'vazio' : sl.valor)));
          s.appendChild(document.createTextNode(' '));
        });
        dec.appendChild(s);
      }
      dec.appendChild(el('p', 'nota', x.formulario_ativo
        ? 'Formulário ativo: ' + x.formulario_ativo + ' — próxima pergunta: ' + ((x.slots_finais || {}).requested_slot || '—')
        : 'Nenhum formulário ativo.'));

      var bd = limpar(document.getElementById('x-banco'));
      var gravou = false;
      ((x.banco || {}).atividades || []).forEach(function (a) {
        gravou = true;
        bd.appendChild(el('pre', 'sql', 'INSERT INTO atividades  →  id=' + a.id + '\n  usuario=' + a.usuario + '  tipo=' + a.tipo +
          '  duracao=' + (a.duracao === null ? 'NULL' : a.duracao) + '  intensidade=' + (a.intensidade === null ? 'NULL' : a.intensidade) +
          '\n  data=' + a.data + '  hora=' + a.hora));
      });
      ((x.banco || {}).agenda || []).forEach(function (a) {
        gravou = true;
        bd.appendChild(el('pre', 'sql', 'INSERT INTO agenda  →  id=' + a.id + '\n  usuario=' + a.usuario + '  tipo=' + a.tipo +
          '  data=' + a.data + '  hora=' + (a.hora === null ? 'NULL' : a.hora)));
      });
      if (!gravou) bd.appendChild(el('p', 'nota', 'Nada foi gravado no banco nesta rodada.'));
      bd.appendChild(el('p', 'nota', 'Resposta devolvida em ' + (x.latencia_ms === undefined ? '—' : x.latencia_ms + ' ms') +
        ' (' + (turno.respostas || []).length + ' mensagem(ns) do bot).'));
    }

    function acenderEtapas() {
      var itens = Array.prototype.slice.call(estacoes.querySelectorAll('.estacao'));
      itens.forEach(function (i) { i.classList.remove('acesa', 'atual'); });
      vazio.hidden = true; estacoes.hidden = false;
      if (passo.checked) {
        filaEtapas = itens.slice(); botaoEtapa.hidden = false; avancarEtapa();
      } else {
        filaEtapas = []; botaoEtapa.hidden = true;
        itens.forEach(function (i, n) { setTimeout(function () { i.classList.add('acesa'); }, 120 + n * 380); });
      }
    }
    function avancarEtapa() {
      var anterior = estacoes.querySelector('.estacao.atual');
      if (anterior) anterior.classList.remove('atual');
      var proxima = filaEtapas.shift();
      if (proxima) { proxima.classList.add('acesa', 'atual'); proxima.scrollIntoView({ block: 'nearest' }); }
      if (!filaEtapas.length) botaoEtapa.hidden = true;
    }
    botaoEtapa.addEventListener('click', avancarEtapa);
    document.addEventListener('keydown', function (ev) {
      if (ev.code === 'Space' && filaEtapas.length && document.activeElement.tagName !== 'INPUT') { ev.preventDefault(); avancarEtapa(); }
    });

    function mostrarTurno(turno) {
      balao('usuario', turno.mensagem, turno.usuario + ' · ' + (turno.momento || ''));
      (turno.respostas || []).forEach(function (r) { balao('bot', r); });
      if (!(turno.respostas || []).length) balao('erro', 'O bot não respondeu a esta mensagem.');
      linhaQuebrou(turno);
      preencherRaioX(turno);
      acenderEtapas();
    }

    if (modo === 'replay') {
      var roteiro = null; var indice = 0;
      var contador = document.getElementById('replay-contador');
      function atualizar() { contador.textContent = roteiro ? ('fala ' + indice + ' de ' + roteiro.turnos.length) : ''; }
      api('/api/replay').then(function (dados) {
        roteiro = dados;
        document.getElementById('replay-origem').textContent =
          'gravada em ' + dados.gravado_em + ' · ' + dados.ambiente + ' · modelo ' + dados.modelo;
        atualizar();
      }).catch(function (e) { document.getElementById('replay-origem').textContent = e.message; });
      document.getElementById('replay-proxima').addEventListener('click', function () {
        if (!roteiro || indice >= roteiro.turnos.length) return;
        mostrarTurno(roteiro.turnos[indice]); indice += 1; atualizar();
      });
      document.getElementById('replay-reiniciar').addEventListener('click', function () {
        indice = 0; limpar(mensagens); estacoes.hidden = true; vazio.hidden = false; atualizar();
      });
      return;
    }

    var campo = document.getElementById('campo');
    function enviar(texto) {
      texto = (texto || '').trim(); if (!texto) return;
      campo.value = ''; campo.disabled = true;
      api('/api/chat', { mensagem: texto, usuario: apelido }).then(mostrarTurno).catch(function (e) {
        balao('usuario', texto, apelido); balao('erro', e.message);
      }).then(function () { campo.disabled = false; campo.focus(); });
    }
    document.getElementById('form-chat').addEventListener('submit', function (ev) { ev.preventDefault(); enviar(campo.value); });
    var sugestoes = document.getElementById('sugestoes');
    ['bom dia', 'bebi água', 'corri 30 minutos intenso', 'malhei 1 hora', 'agendar yoga amanhã às 7h',
      'minha agenda', 'quero registrar uma atividade', 'como estou hoje?', 'tomei um café', 'bebi h2o'
    ].forEach(function (s) {
      var b = el('button', null, s); b.type = 'button';
      b.addEventListener('click', function () { enviar(s); }); sugestoes.appendChild(b);
    });
    campo.focus();
  }

  // =====================================================================
  // MURAL "QUEBRE O BOT"
  // =====================================================================
  function cartao(alvo, valor, rotulo, classe) {
    var c = el('div', 'cartao' + (classe ? ' ' + classe : ''));
    c.appendChild(el('b', null, valor)); c.appendChild(el('span', null, rotulo)); alvo.appendChild(c);
  }
  function iniciarMural() {
    function carregar() {
      api('/api/mural').then(function (d) {
        var r = d.resumo; var resumo = limpar(document.getElementById('mural-resumo'));
        cartao(resumo, r.total, 'falas enviadas ao bot');
        cartao(resumo, r.quebras, 'falhas no mural');
        cartao(resumo, pct(r.taxa_quebra), 'taxa de falha');
        cartao(resumo, r.latencia_media_ms + ' ms', 'latência média');
        var rank = limpar(document.getElementById('mural-ranking'));
        r.ranking.forEach(function (i) { rank.appendChild(el('li', null, i.usuario + ' — ' + i.quebras)); });
        if (!r.ranking.length) rank.appendChild(el('li', 'dica', 'ninguém ainda'));
        var lista = limpar(document.getElementById('mural-lista'));
        d.quebras.forEach(function (q) {
          var item = el('div', 'quebra');
          item.appendChild(el('div', 'fala', '“' + q.texto + '”'));
          var linha = el('div', 'dica', q.usuario + ' · ' + q.momento.replace('T', ' ') + ' · intent: ' + (q.intent || '—') +
            ' (' + pct(q.confianca) + ') ');
          if (q.motivo_auto) linha.appendChild(el('span', 'selo', q.motivo_auto));
          if (q.quebra_reportada) linha.appendChild(el('span', 'selo', 'reportado' + (q.comentario ? ': ' + q.comentario : '')));
          item.appendChild(linha);
          item.appendChild(el('div', 'resp', 'bot: ' + (q.resposta || '(sem resposta)')));
          lista.appendChild(item);
        });
        if (!d.quebras.length) lista.appendChild(el('p', 'dica', 'Nenhuma falha ainda. Vá ao chat e tente: “tomei um café”, “bebi h2o”, “valeu, fui”.'));
      }).catch(function () { /* tenta de novo no proximo ciclo */ });
    }
    carregar(); setInterval(carregar, 4000);
  }

  // =====================================================================
  // DUELO 1.0 x 2.0
  // =====================================================================
  function iniciarDuelo() {
    var ultimo = null;
    var campo = document.getElementById('campo-duelo');
    var salvar = document.getElementById('duelo-salvar');
    var status = document.getElementById('duelo-status');

    function par(alvo, rotulo, valor) {
      var p = el('p'); p.appendChild(el('span', 'dica', rotulo + ' ')); p.appendChild(el('span', 'mono', valor)); alvo.appendChild(p);
    }
    function mostrar(d, gravado) {
      ultimo = d;
      var rasa = limpar(document.getElementById('duelo-rasa'));
      if (d.rasa.ok) {
        rasa.appendChild(barras(d.rasa.ranking, d.rasa.intent, true));
        par(rasa, 'entidades:', d.rasa.entidades.length ? d.rasa.entidades.map(function (e) { return e.entidade + '=' + e.valor; }).join('  ') : 'nenhuma');
        par(rasa, 'tempo:', d.rasa.latencia_ms + ' ms · custo por chamada: zero (modelo local)');
      } else rasa.appendChild(el('p', 'selo', d.rasa.erro));

      var llm = limpar(document.getElementById('duelo-llm'));
      if (d.llm.ok) {
        var s = d.llm.estrutura || {};
        par(llm, 'intenção:', s.intencao);
        par(llm, 'tipo_atividade:', s.tipo_atividade === null ? 'null' : s.tipo_atividade);
        par(llm, 'duracao_min:', s.duracao_min === null ? 'null' : s.duracao_min);
        par(llm, 'intensidade:', s.intensidade === null ? 'null' : s.intensidade);
        par(llm, 'quando:', s.quando === null ? 'null' : s.quando);
        llm.appendChild(el('div', 'balao bot', s.resposta || ''));
        par(llm, 'tempo:', d.llm.latencia_ms + ' ms · modelo: ' + d.llm.modelo + ' · prompt: ' + d.llm.versao_prompt);
      } else llm.appendChild(el('p', d.llm.configurado ? 'selo' : 'dica', d.llm.erro));
      status.textContent = gravado ? 'GRAVAÇÃO de ' + (d.momento || '').replace('T', ' ') + ' — não é uma chamada ao vivo.' : '';
      salvar.hidden = gravado || !(d.rasa.ok && d.llm.ok);
    }
    function duelar(texto) {
      texto = (texto || '').trim(); if (!texto) return;
      campo.value = texto; status.textContent = 'consultando os dois lados…';
      api('/api/duelo', { mensagem: texto }).then(function (d) { mostrar(d, false); })
        .catch(function (e) { status.textContent = e.message; });
    }
    document.getElementById('form-duelo').addEventListener('submit', function (ev) { ev.preventDefault(); duelar(campo.value); });
    var sug = document.getElementById('sugestoes-duelo');
    ['tomei um café', 'malhei 1 hora', 'bebi h2o', 'valeu, fui', 'dei uma corridinha de meia hora no parque', 'agendar yoga amanhã às 7h']
      .forEach(function (s) { var b = el('button', null, s); b.type = 'button'; b.addEventListener('click', function () { duelar(s); }); sug.appendChild(b); });
    function listarGravados() {
      api('/api/duelo/gravados').then(function (lista) {
        var alvo = limpar(document.getElementById('duelos-gravados'));
        lista.forEach(function (g) {
          var b = el('button', 'botao', g.mensagem); b.type = 'button';
          b.addEventListener('click', function () { campo.value = g.mensagem; mostrar(g, true); }); alvo.appendChild(b);
        });
        if (!lista.length) alvo.appendChild(el('span', 'dica', 'Nenhum duelo gravado nesta instalação.'));
      });
    }
    salvar.addEventListener('click', function () {
      api('/api/duelo/gravados', ultimo).then(function () { status.textContent = 'Duelo salvo.'; salvar.hidden = true; listarGravados(); })
        .catch(function (e) { status.textContent = e.message; });
    });
    listarGravados();
  }

  // =====================================================================
  // DASHBOARD
  // =====================================================================
  function iniciarDashboard() {
    var turma = document.getElementById('dash-turma');
    var filtro = document.getElementById('dash-filtro');
    var recentes = [];
    function barrasContagem(alvo, mapa, cor) {
      limpar(alvo);
      var chaves = Object.keys(mapa); var maximo = Math.max.apply(null, chaves.map(function (k) { return mapa[k]; }).concat([1]));
      chaves.forEach(function (k) {
        var linha = el('div', 'barra-linha'); linha.appendChild(el('span', 'nome', k));
        var trilho = el('div', 'trilho'); var cheio = el('i'); cheio.style.width = (mapa[k] / maximo * 100) + '%';
        if (cor) cheio.style.background = cor; trilho.appendChild(cheio); linha.appendChild(trilho);
        linha.appendChild(el('span', 'pct', mapa[k])); alvo.appendChild(linha);
      });
      if (!chaves.length) alvo.appendChild(el('p', 'dica', 'Sem dados no período.'));
    }
    function desenharTabela() {
      var corpo = limpar(document.querySelector('#dash-tabela tbody')); var termo = filtro.value.toLowerCase();
      recentes.filter(function (a) { return !termo || (a.tipo + ' ' + a.data + ' ' + a.usuario + ' ' + (a.intensidade || '')).toLowerCase().indexOf(termo) >= 0; })
        .forEach(function (a) {
          var tr = el('tr');
          [a.data, a.hora, a.tipo, a.duracao ? Math.round(a.duracao) + ' min' : '—', a.intensidade || '—', a.usuario]
            .forEach(function (v) { tr.appendChild(el('td', null, v)); });
          corpo.appendChild(tr);
        });
    }
    function carregar() {
      var q = turma.checked ? '' : '?usuario=' + encodeURIComponent(apelido);
      document.getElementById('dash-csv').href = '/api/export.csv' + q;
      api('/api/dashboard' + q).then(function (d) {
        var c = limpar(document.getElementById('dash-cartoes'));
        cartao(c, d.hoje.total, 'atividades hoje');
        cartao(c, d.semana.total, 'nos últimos 7 dias');
        cartao(c, d.semana.media_dia.toFixed(1), 'média por dia');
        cartao(c, d.sequencia, d.sequencia === 1 ? 'dia seguido' : 'dias seguidos');
        cartao(c, Math.round(d.semana.tempo_total) + ' min', 'tempo em 7 dias');
        var serie = limpar(document.getElementById('dash-serie'));
        var maximo = Math.max.apply(null, d.serie.map(function (p) { return p[1]; }).concat([1]));
        d.serie.forEach(function (p, i) {
          var dia = el('div', 'dia' + (i === d.serie.length - 1 ? ' hoje' : ''));
          dia.appendChild(el('span', 'n', p[1])); var col = el('div', 'col'); col.style.height = (p[1] / maximo * 78) + '%';
          dia.appendChild(col); dia.appendChild(el('span', null, p[0].slice(8) + '/' + p[0].slice(5, 7))); serie.appendChild(dia);
        });
        barrasContagem(document.getElementById('dash-tipos'), d.semana.por_tipo);
        barrasContagem(document.getElementById('dash-intensidade'), d.semana.por_intensidade, 'var(--core)');
        var ag = limpar(document.getElementById('dash-agenda'));
        d.agenda.forEach(function (a) { ag.appendChild(el('li', null, a.data.slice(8) + '/' + a.data.slice(5, 7) + (a.hora ? ' ' + a.hora : '') + ' — ' + a.tipo + (turma.checked ? ' (' + a.usuario + ')' : ''))); });
        if (!d.agenda.length) ag.appendChild(el('li', 'dica', 'Nada agendado.'));
        recentes = d.recentes; desenharTabela();
      });
    }
    turma.addEventListener('change', carregar); filtro.addEventListener('input', desenharTabela);
    carregar(); setInterval(carregar, 6000);
  }

  // =====================================================================
  // SAUDE (observabilidade)
  // =====================================================================
  function iniciarSaude() {
    function carregar() {
      api('/api/saude').then(function (d) {
        var s = limpar(document.getElementById('saude-servicos'));
        cartao(s, 'no ar', 'Interface web (Flask)', 'ok');
        cartao(s, d.rasa.no_ar ? 'no ar' : 'fora', 'Rasa Server · ' + (d.rasa.modelo || 'sem modelo'), d.rasa.no_ar ? 'ok' : 'fora');
        cartao(s, d.actions.no_ar ? 'no ar' : 'fora', 'Action Server', d.actions.no_ar ? 'ok' : 'fora');
        cartao(s, d.llm.configurado ? 'ligado' : 'desligado', 'LLM do duelo' + (d.llm.configurado ? ' · ' + d.llm.modelo : ''), d.llm.configurado ? 'ok' : '');
        cartao(s, d.replay_disponivel ? 'pronto' : 'ausente', 'Replay gravado', d.replay_disponivel ? 'ok' : 'fora');
        var u = limpar(document.getElementById('saude-uso'));
        cartao(u, d.interacoes.total, 'falas processadas');
        cartao(u, d.interacoes.latencia_media_ms + ' ms', 'latência média');
        cartao(u, pct(d.interacoes.taxa_quebra), 'taxa de falha');
        cartao(u, d.llm.configurado && d.llm.externo ? 'por chamada' : 'zero', 'custo de API');
      });
    }
    carregar(); setInterval(carregar, 5000);
  }

  if (pagina === 'chat' || pagina === 'replay') iniciarChat();
  if (pagina === 'mural') iniciarMural();
  if (pagina === 'duelo') iniciarDuelo();
  if (pagina === 'dashboard') iniciarDashboard();
  if (pagina === 'saude') iniciarSaude();
})();
