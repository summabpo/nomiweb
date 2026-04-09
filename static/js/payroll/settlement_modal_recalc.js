/**
 * Igual que templates/payroll/partials/settlement_recalc_js.html (collectstatic/S3).
 */
(function (global) {
  'use strict';

  var RECALC_TRIGGER_IDS = {
    dias_cesantias: 1,
    dias_primas: 1,
    dias_vacaciones: 1,
    dias_susp_vac: 1,
    dias_susp_ces: 1,
    base_cesantias: 1,
    base_primas: 1,
    base_vacaciones: 1,
    valor_indemnizacion: 1,
  };

  function parseSettlementNumber(el) {
    if (!el) return 0;
    var s = String(el.value != null ? el.value : '').trim();
    if (!s) return 0;
    if (s.indexOf(',') !== -1) {
      s = s.replace(/\./g, '').replace(',', '.');
    }
    var n = parseFloat(s);
    return isFinite(n) ? n : 0;
  }

  function getById(root, id) {
    return root.querySelector('#' + id);
  }

  function getNumber(root, id) {
    return parseSettlementNumber(getById(root, id));
  }

  function setIntegerField(root, id, value) {
    var el = getById(root, id);
    if (el) el.value = Math.ceil(Number(value) || 0);
  }

  function setTruncField(root, id, value) {
    var el = getById(root, id);
    if (el) el.value = Math.trunc(Number(value) || 0);
  }

  function setVacDaysField(root, id, value) {
    var el = getById(root, id);
    if (!el) return;
    var f = Number(value);
    if (!isFinite(f)) f = 0;
    if (f < 0) f = 0;
    el.value = f.toFixed(2);
  }

  function snapSettlementBaselines(modalContent) {
    var form = modalContent.querySelector('#form_settlement_new, #form_settlement_edit');
    if (!form) return;
    var dc = Math.trunc(getNumber(modalContent, 'dias_cesantias'));
    var sc = Math.trunc(getNumber(modalContent, 'dias_susp_ces'));
    form.dataset.nomiwebGrossCesDias = String(Math.max(0, dc + sc));
    var v = getNumber(modalContent, 'dias_vacaciones');
    var sv = getNumber(modalContent, 'dias_susp_vac');
    form.dataset.nomiwebVacBaselineVac = String(v);
    form.dataset.nomiwebVacBaselineSuspVac = String(sv);
  }

  function updateGrossCesFromEffective(modalContent, form) {
    if (!form) return;
    var dc = Math.trunc(getNumber(modalContent, 'dias_cesantias'));
    var sc = Math.trunc(getNumber(modalContent, 'dias_susp_ces'));
    form.dataset.nomiwebGrossCesDias = String(Math.max(0, dc + sc));
  }

  function syncDiasCesantiasFromSusp(modalContent, form) {
    if (!form) return;
    var G = parseInt(form.dataset.nomiwebGrossCesDias, 10);
    if (!isFinite(G) || G < 0) {
      G = Math.trunc(getNumber(modalContent, 'dias_cesantias')) +
        Math.trunc(getNumber(modalContent, 'dias_susp_ces'));
      form.dataset.nomiwebGrossCesDias = String(Math.max(0, G));
    }
    var susp = Math.trunc(getNumber(modalContent, 'dias_susp_ces'));
    var newEff = Math.max(0, G - susp);
    setTruncField(modalContent, 'dias_cesantias', newEff);
  }

  function snapVacBaselineFromFields(modalContent, form) {
    if (!form) return;
    form.dataset.nomiwebVacBaselineVac = String(getNumber(modalContent, 'dias_vacaciones'));
    form.dataset.nomiwebVacBaselineSuspVac = String(getNumber(modalContent, 'dias_susp_vac'));
  }

  function syncDiasVacacionesFromSuspVac(modalContent, form) {
    if (!form) return;
    var v0 = parseFloat(form.dataset.nomiwebVacBaselineVac);
    var s0 = parseFloat(form.dataset.nomiwebVacBaselineSuspVac);
    if (!isFinite(v0) || !isFinite(s0)) {
      v0 = getNumber(modalContent, 'dias_vacaciones');
      s0 = getNumber(modalContent, 'dias_susp_vac');
      form.dataset.nomiwebVacBaselineVac = String(v0);
      form.dataset.nomiwebVacBaselineSuspVac = String(s0);
    }
    var s = getNumber(modalContent, 'dias_susp_vac');
    var newV = v0 - (s - s0) * (15 / 360);
    setVacDaysField(modalContent, 'dias_vacaciones', newV);
  }

  function recalculateSettlementTotals(modalContent) {
    if (!modalContent || !getById(modalContent, 'dias_cesantias')) return;

    var diasCes = Math.trunc(getNumber(modalContent, 'dias_cesantias'));
    var diasPri = Math.trunc(getNumber(modalContent, 'dias_primas'));
    var diasVac = getNumber(modalContent, 'dias_vacaciones');

    var baseCes = getNumber(modalContent, 'base_cesantias');
    var basePri = getNumber(modalContent, 'base_primas');
    var baseVac = getNumber(modalContent, 'base_vacaciones');

    var cesantias = Math.ceil((baseCes * diasCes) / 360);
    var prima = Math.ceil((diasPri / 360) * basePri);
    var vacaciones = Math.ceil((baseVac * diasVac) / 30);
    var intereses = Math.ceil(cesantias * 0.12 * (diasCes / 360));

    setIntegerField(modalContent, 'valor_cesantias', cesantias);
    setIntegerField(modalContent, 'valor_intereses', intereses);
    setIntegerField(modalContent, 'valor_prima', prima);
    setIntegerField(modalContent, 'valor_vacaciones', vacaciones);

    var indemnizacion = getNumber(modalContent, 'valor_indemnizacion');
    var total = Math.round(
      cesantias + intereses + prima + vacaciones + indemnizacion
    );
    var totalEl = getById(modalContent, 'total_liquidacion');
    if (totalEl) totalEl.value = total;
  }

  function bindSettlementRecalc(modalContent) {
    if (!modalContent || !getById(modalContent, 'dias_cesantias')) return;

    function delegatedRecalc(ev) {
      var t = ev.target;
      if (!t || !t.id) return;
      var form = modalContent.querySelector('#form_settlement_new, #form_settlement_edit');
      if (!form) return;

      if (t.id === 'dias_susp_ces') {
        syncDiasCesantiasFromSusp(modalContent, form);
      } else if (t.id === 'dias_cesantias') {
        updateGrossCesFromEffective(modalContent, form);
      } else if (t.id === 'dias_susp_vac') {
        syncDiasVacacionesFromSuspVac(modalContent, form);
      } else if (t.id === 'dias_vacaciones') {
        snapVacBaselineFromFields(modalContent, form);
      }

      if (!RECALC_TRIGGER_IDS[t.id]) return;
      recalculateSettlementTotals(modalContent);
    }

    if (modalContent._nomiwebSettlementRecalcHandler) {
      modalContent.removeEventListener('input', modalContent._nomiwebSettlementRecalcHandler, true);
      modalContent.removeEventListener('change', modalContent._nomiwebSettlementRecalcHandler, true);
    }
    modalContent._nomiwebSettlementRecalcHandler = delegatedRecalc;
    modalContent.addEventListener('input', delegatedRecalc, true);
    modalContent.addEventListener('change', delegatedRecalc, true);

    snapSettlementBaselines(modalContent);
  }

  global.NomiwebSettlementRecalc = {
    bind: bindSettlementRecalc,
    recalculate: recalculateSettlementTotals,
    snapBaselines: snapSettlementBaselines,
  };
})(window);
