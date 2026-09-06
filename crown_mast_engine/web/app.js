"use strict";

const state = {
  metadata: null,
  builds: new Map(),
  report: null,
  batch: null,
};

const $ = (selector) => document.querySelector(selector);
const form = $("#calculator-form");
const buildRows = $("#build-rows");

const outcomeLabels = {
  tie_band: "사실상 동률",
  marginal_funnel: "몰아주기 근소 우세",
  clear_funnel: "몰아주기 우세",
};

function outcomeLabel(outcome, baselineLabel) {
  if (outcome === "clear_conventional") return `${baselineLabel} 우세`;
  if (outcome === "marginal_conventional") return `${baselineLabel} 근소 우세`;
  return outcomeLabels[outcome] || outcome;
}

function applyBaselineText(label) {
  document.querySelectorAll("[data-baseline-template]").forEach((element) => {
    element.textContent = element.dataset.baselineTemplate.replace("{baseline}", label);
  });
}

const actorRole = (actor) => {
  if (actor === $("#b1-select").value) return "BURST I";
  if (actor === "crown" || actor === "mast-romantic-maid") return "BURST II";
  return actor === $("#main-b3-select").value ? "MAIN B3" : "SUB B3";
};

function optionLabel(character) {
  return `${character.name} · ${character.element} ${character.weapon_type}`;
}

function fillSelect(select, options) {
  select.replaceChildren(...options.map((character) => {
    const option = document.createElement("option");
    option.value = character.slug;
    option.textContent = optionLabel(character);
    return option;
  }));
}

function defaultBuild() {
  const gear = state.metadata.defaults.gear_state;
  return {
    gear_states: { slot_1: gear, slot_2: gear, slot_3: gear, slot_4: gear },
    collection_stage: "none",
    atk_lines: 0,
    element_lines: 0,
    ammo_lines: 0,
  };
}

function currentActors() {
  return [
    $("#b1-select").value,
    "crown",
    "mast-romantic-maid",
    $("#main-b3-select").value,
    $("#secondary-b3-select").value,
  ];
}

function saveVisibleBuilds() {
  buildRows.querySelectorAll(".build-row").forEach((row) => {
    state.builds.set(row.dataset.actor, {
      gear_states: Object.fromEntries([...row.querySelectorAll("[data-slot]")].map((select) => [select.dataset.slot, select.value])),
      collection_stage: row.querySelector("[data-field='collection_stage']").value,
      atk_lines: Number(row.querySelector("[data-field='atk_lines']").value),
      element_lines: Number(row.querySelector("[data-field='element_lines']").value),
      ammo_lines: Number(row.querySelector("[data-field='ammo_lines']").value),
    });
  });
}

function renderBuildRows() {
  saveVisibleBuilds();
  const bySlug = new Map(state.metadata.characters.map((item) => [item.slug, item]));
  buildRows.replaceChildren(...currentActors().map((actor) => {
    const character = bySlug.get(actor);
    const build = state.builds.get(actor) || defaultBuild();
    if (!state.builds.has(actor)) {
      build.collection_stage = state.metadata.defaults.collection_by_actor[actor];
    }
    state.builds.set(actor, build);
    const row = document.createElement("div");
    row.className = "build-row";
    row.dataset.actor = actor;
    row.innerHTML = `
      <div class="build-actor" title="${character.name}">
        <strong>${character.name}</strong><span>${actorRole(actor)}</span>
      </div>
      <select data-field="collection_stage" aria-label="${character.name} 소장품"></select>
      <input data-field="atk_lines" type="number" min="0" step="1" aria-label="${character.name} 공격력 옵션 줄 수">
      <input data-field="element_lines" type="number" min="0" step="1" aria-label="${character.name} 우월 코드 옵션 줄 수">
      <input data-field="ammo_lines" type="number" min="0" step="1" aria-label="${character.name} 최대 장탄 옵션 줄 수">
      <div class="gear-slots">
        ${[1, 2, 3, 4].map((slot) => `<label><span>S${slot}</span><select data-slot="slot_${slot}" aria-label="${character.name} 장비 슬롯 ${slot}"><option value="base5">B5</option><option value="ol0">O0</option><option value="ol5">O5</option></select></label>`).join("")}
      </div>
    `;
    const collectionSelect = row.querySelector("[data-field='collection_stage']");
    collectionSelect.replaceChildren(...state.metadata.collection_stages.map((stage) => {
      const option = document.createElement("option");
      option.value = stage;
      option.textContent = stage === "none" ? "없음" : stage;
      return option;
    }));
    collectionSelect.value = build.collection_stage;
    row.querySelectorAll("[data-slot]").forEach((select) => { select.value = build.gear_states[select.dataset.slot]; });
    for (const field of ["atk_lines", "element_lines", "ammo_lines"]) {
      row.querySelector(`[data-field='${field}']`).value = build[field];
    }
    return row;
  }));
}

function syncB3Options(changed) {
  const main = $("#main-b3-select");
  const secondary = $("#secondary-b3-select");
  if (main.value === secondary.value) {
    const target = changed === main ? secondary : main;
    const replacement = [...target.options].find((option) => option.value !== changed.value);
    if (replacement) target.value = replacement.value;
  }
  [...main.options].forEach((option) => { option.disabled = option.value === secondary.value; });
  [...secondary.options].forEach((option) => { option.disabled = option.value === main.value; });
  renderBuildRows();
}

function setDefaults() {
  const defaults = state.metadata.defaults;
  $("#b1-select").value = defaults.roster.b1;
  $("#main-b3-select").value = defaults.roster.main_b3;
  $("#secondary-b3-select").value = defaults.roster.secondary_b3;
  $("#boss-def").value = defaults.combat.boss_def;
  $("#boss-element").value = defaults.combat.boss_element || "";
  $("#core-rate").value = defaults.combat.core_hit_rate_pct;
  $("#range-bonus").value = defaults.combat.range_bonus_pct;
  const baseline = document.querySelector(`input[name="baseline-rotation"][value="${defaults.baseline_rotation}"]`);
  if (baseline) baseline.checked = true;
  state.builds.clear();
  buildRows.replaceChildren();
  syncB3Options($("#main-b3-select"));
}

function collectPayload() {
  saveVisibleBuilds();
  return {
    roster: {
      b1: $("#b1-select").value,
      main_b3: $("#main-b3-select").value,
      secondary_b3: $("#secondary-b3-select").value,
    },
    builds: Object.fromEntries(currentActors().map((actor) => [actor, state.builds.get(actor)])),
    baseline_rotation: document.querySelector('input[name="baseline-rotation"]:checked').value,
    combat: {
      boss_def: Number($("#boss-def").value),
      boss_element: $("#boss-element").value || null,
      core_hit_rate_pct: Number($("#core-rate").value),
      range_bonus_pct: Number($("#range-bonus").value),
    },
  };
}

const damageFormat = new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 0 });
const compactFormat = new Intl.NumberFormat("ko-KR", { notation: "compact", maximumFractionDigits: 2 });
const formatDamage = (value) => damageFormat.format(value);
const signedDamage = (value) => value == null ? "-" : `${value >= 0 ? "+" : ""}${damageFormat.format(value)}`;
const formatCompact = (value) => compactFormat.format(value);
const formatPercent = (value, digits = 2) => value == null ? "-" : `${(value * 100).toFixed(digits)}%`;
const signedPercent = (value) => value == null ? "-" : `${value >= 0 ? "+" : ""}${(value * 100).toFixed(3)}%`;
const percentagePoint = (value) => value == null ? "-" : `${value >= 0 ? "+" : ""}${(value * 100).toFixed(2)}%p`;
const fileDate = () => {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
};

function percentRange(stats, signed = false) {
  if (!stats || stats.minimum == null || stats.maximum == null) return "-";
  const formatter = signed ? signedPercent : formatPercent;
  return `${formatter(stats.minimum)} ~ ${formatter(stats.maximum)}`;
}

function renderReport(report) {
  state.report = report;
  const crown = report.comparisons.crown_entry;
  const mast = report.comparisons.mast_entry;
  const crownOverall = crown.overall;
  const mastOverall = mast.overall;
  const mainActor = report.scenario.main_actor;
  const mainName = report.display_names[mainActor];

  $("#result-title").textContent = `${mainName} 네 운용 비교`;
  $("#crown-conventional-total").textContent = formatDamage(crownOverall.team.conventional);
  $("#mast-conventional-total").textContent = formatDamage(mastOverall.team.conventional);
  $("#crown-funnel-total").textContent = formatDamage(crownOverall.team.funnel);
  $("#mast-funnel-total").textContent = formatDamage(mastOverall.team.funnel);
  $("#crown-conventional-share").textContent = `Main ${formatPercent(crownOverall.conventional_main_share)}`;
  $("#mast-conventional-share").textContent = `Main ${formatPercent(mastOverall.conventional_main_share)}`;
  $("#crown-funnel-share").textContent = `Main ${formatPercent(crownOverall.funnel_main_share)}`;
  $("#mast-funnel-share").textContent = `Main ${formatPercent(mastOverall.funnel_main_share)}`;

  renderStrategyComparison("crown", crownOverall, "크크메");
  renderStrategyComparison("mast", mastOverall, "진입 메크메");

  const conventionalEntry = report.entry_effects.conventional.team;
  const funnelEntry = report.entry_effects.funnel.team;
  $("#conventional-entry-change").textContent = signedPercent(conventionalEntry.relative_change);
  $("#conventional-entry-change").className = valueClass(conventionalEntry.relative_change);
  $("#conventional-entry-delta").textContent = signedDamage(conventionalEntry.delta_mast_minus_crown);
  $("#funnel-entry-change").textContent = signedPercent(funnelEntry.relative_change);
  $("#funnel-entry-change").className = valueClass(funnelEntry.relative_change);
  $("#funnel-entry-delta").textContent = signedDamage(funnelEntry.delta_mast_minus_crown);

  const firstBurst = report.first_burst_entry_comparison;
  $("#first-burst-window").textContent = `c${firstBurst.cycle} · ${firstBurst.window_start.toFixed(1)}s ≤ t < ${firstBurst.window_end.toFixed(1)}s`;
  $("#first-crown-total").textContent = formatDamage(firstBurst.team.crown_entry);
  $("#first-mast-total").textContent = formatDamage(firstBurst.team.mast_entry);
  $("#first-entry-delta").textContent = signedDamage(firstBurst.team.delta_mast_minus_crown);
  $("#first-entry-delta").className = firstBurst.team.delta_mast_minus_crown > 0 ? "positive" : firstBurst.team.delta_mast_minus_crown < 0 ? "negative" : "";
  $("#first-entry-change").textContent = signedPercent(firstBurst.team.relative_change);
  $("#first-entry-change").className = firstBurst.team.relative_change > 0 ? "positive" : firstBurst.team.relative_change < 0 ? "negative" : "";
  $("#first-burst-character-body").replaceChildren(...Object.entries(firstBurst.by_character).map(([actor, item]) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${report.display_names[actor]}</td><td>${formatDamage(item.crown_entry)}</td><td>${formatDamage(item.mast_entry)}</td><td class="${item.delta_mast_minus_crown > 0 ? "positive" : item.delta_mast_minus_crown < 0 ? "negative" : ""}">${signedDamage(item.delta_mast_minus_crown)}</td><td>${signedPercent(item.relative_change)}</td>`;
    return row;
  }));

  $("#four-character-body").replaceChildren(...Object.keys(crown.by_character).map((actor) => {
    const crownItem = crown.by_character[actor];
    const mastItem = mast.by_character[actor];
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${report.display_names[actor]}</td>
      ${rotationCell(crownItem.damage.conventional, crownItem.conventional_share)}
      ${rotationCell(mastItem.damage.conventional, mastItem.conventional_share)}
      ${rotationCell(crownItem.damage.funnel, crownItem.funnel_share)}
      ${rotationCell(mastItem.damage.funnel, mastItem.funnel_share)}
    `;
    return row;
  }));

  renderMacroCycles("#crown-cycle-body", crown.macro_cycles);
  renderMacroCycles("#mast-cycle-body", mast.macro_cycles);

  const signature = report.mechanics_signature;
  $("#mechanics-revision").textContent = `${signature.engine_rule_revision} · ${signature.skill_hook_revision}`;
  $("#results").hidden = false;
}

function valueClass(value) {
  return value > 0 ? "positive" : value < 0 ? "negative" : "";
}

function renderStrategyComparison(prefix, overall, baselineLabel) {
  const outcome = overall.outcome_band;
  const card = $(`#${prefix}-comparison-card`);
  card.className = `strategy-comparison-card ${outcome.includes("conventional") ? "conventional" : outcome.includes("funnel") ? "funnel" : "tie"}`;
  $(`#${prefix}-verdict`).textContent = outcomeLabel(outcome, baselineLabel);
  $(`#${prefix}-funnel-change`).textContent = signedPercent(overall.team.relative_change);
  $(`#${prefix}-funnel-change`).className = valueClass(overall.team.relative_change);
  $(`#${prefix}-main-share`).textContent = formatPercent(overall.conventional_main_share);
  $(`#${prefix}-break-even`).textContent = formatPercent(overall.break_even_main_share_c);
}

function rotationCell(damage, share) {
  return `<td><strong>${formatDamage(damage)}</strong><small>${formatPercent(share)}</small></td>`;
}

function renderMacroCycles(selector, cycles) {
  $(selector).replaceChildren(...Object.entries(cycles).map(([cycle, item]) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${cycle}</td><td>${formatDamage(item.team.conventional)}</td><td>${formatDamage(item.team.funnel)}</td><td class="${valueClass(item.team.relative_change)}">${signedPercent(item.team.relative_change)}</td>`;
    return row;
  }));
}

function batchRequestPayload() {
  const payload = collectPayload();
  return { roster: payload.roster, combat: payload.combat, baseline_rotation: payload.baseline_rotation };
}

function pointShape(profile) {
  return {
    "equal-o5": "shape-equal",
    "gap-o5-o0": "shape-gap",
    "atk3-vs-b5": "shape-atk",
    "ammo2-vs-o5": "shape-ammo",
  }[profile] || "shape-equal";
}

function selectBatchResult(result) {
  document.querySelectorAll(".sample-point").forEach((point) => point.classList.toggle("selected", point.dataset.caseId === result.case_id));
  document.querySelectorAll("#batch-table-body tr").forEach((row) => row.classList.toggle("selected", row.dataset.caseId === result.case_id));
  const summary = result.summary;
  $("#sample-detail-title").textContent = `${result.labels.b1_label} · ${result.labels.dealer_label}`;
  $("#sample-detail-outcome").textContent = outcomeLabel(summary.outcome_band, state.batch.baseline_label);
  $("#sample-x").textContent = formatPercent(summary.conventional_main_share);
  $("#sample-y").textContent = signedPercent(summary.relative_change);
  $("#sample-break-even").textContent = formatPercent(summary.break_even_main_share_c);
  $("#sample-margin").textContent = summary.margin == null ? "-" : `${summary.margin >= 0 ? "+" : ""}${(summary.margin * 100).toFixed(2)}%p`;
  $("#batch-detail-shares").replaceChildren(...Object.entries(summary.character_shares).map(([actor, shares]) => {
    const item = document.createElement("div");
    item.className = "detail-share";
    item.innerHTML = `<strong title="${state.batch.display_names[actor]}">${state.batch.display_names[actor]}</strong><span>기준 ${formatPercent(shares.conventional)} · 몰아주기 ${formatPercent(shares.funnel)}</span>`;
    return item;
  }));
  $("#sample-c-total").textContent = formatDamage(summary.conventional_damage);
  $("#sample-f-total").textContent = formatDamage(summary.funnel_damage);
  $("#sample-g").textContent = signedPercent(summary.g);
  $("#sample-l").textContent = formatPercent(summary.l, 3);
  $("#sample-slope").textContent = formatPercent(summary.local_slope, 3);
  $("#sample-lambda").textContent = summary.lambda_star == null ? "-" : summary.lambda_star.toFixed(4);
  $("#selected-character-body").replaceChildren(...Object.entries(result.report.by_character).map(([actor, item]) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${state.batch.display_names[actor]}</td><td>${formatDamage(item.damage.conventional)}</td><td>${formatPercent(item.conventional_share)}</td><td>${formatDamage(item.damage.funnel)}</td><td>${formatPercent(item.funnel_share)}</td><td class="${item.damage.relative_change > 0 ? "positive" : item.damage.relative_change < 0 ? "negative" : ""}">${signedPercent(item.damage.relative_change)}</td>`;
    return row;
  }));
}

function caseLabel(item) {
  return `${item.labels.b1_label} · ${item.labels.dealer_label}`;
}

function renderAggregate(batch) {
  const aggregate = batch.aggregate;
  const outcomes = aggregate.outcomes;
  const extremes = aggregate.extremes;
  const closest = extremes.closest_to_break_even;
  const mainName = batch.display_names[batch.results[0].summary.main_actor];
  const baselineLabel = batch.baseline_label;
  let title;
  if (outcomes.bands.clear_conventional === aggregate.sample_count) title = `모든 기준점에서 명확한 ${baselineLabel} 우세`;
  else if (outcomes.conventional_wins === aggregate.sample_count) title = `모든 기준점에서 ${baselineLabel} 우세`;
  else if (outcomes.bands.clear_funnel === aggregate.sample_count) title = "모든 기준점에서 명확한 몰아주기 우세";
  else if (outcomes.funnel_wins === aggregate.sample_count) title = "모든 기준점에서 몰아주기 우세";
  else title = `${baselineLabel} ${outcomes.conventional_wins}점 · 몰아주기 ${outcomes.funnel_wins}점 · 동률 ${outcomes.tie_band}점`;
  $("#batch-conclusion-title").textContent = title;
  const favorable = extremes.most_funnel_favorable;
  $("#batch-conclusion-text").textContent = `몰아주기에 가장 유리한 조건은 ${caseLabel(favorable)}로 총딜 ${signedPercent(favorable.relative_change)}다.${closest ? ` 손익분기 최근접점에서도 ${mainName} 비중 ${formatPercent(closest.conventional_main_share)}, 추정 분기 ${formatPercent(closest.break_even_main_share_c)}, 간극 ${percentagePoint(closest.margin)}다.` : " 이 배치에서는 유효한 비중 손익분기를 계산할 수 없다."}`;
  $("#aggregate-change-range").textContent = percentRange(aggregate.relative_change, true);
  $("#aggregate-change-average").textContent = `평균 ${signedPercent(aggregate.relative_change.average)}`;
  $("#aggregate-share-range").textContent = percentRange(aggregate.conventional_main_share);
  $("#aggregate-share-average").textContent = `평균 ${formatPercent(aggregate.conventional_main_share.average)}`;
  $("#aggregate-break-even-range").textContent = percentRange(aggregate.break_even_main_share_c);
  $("#aggregate-break-even-average").textContent = `평균 ${formatPercent(aggregate.break_even_main_share_c.average)}`;
  $("#aggregate-margin-range").textContent = aggregate.margin.minimum == null ? "-" : `${percentagePoint(aggregate.margin.minimum)} ~ ${percentagePoint(aggregate.margin.maximum)}`;
  $("#aggregate-margin-average").textContent = `평균 ${percentagePoint(aggregate.margin.average)}`;

  const condition = aggregate.conditions;
  const roster = condition.roster;
  $("#scope-roster").textContent = [roster.b1, roster.crown, roster.mast, roster.main_b3, roster.secondary_b3].map((actor) => batch.display_names[actor]).join(" / ");
  $("#scope-main").textContent = batch.display_names[roster.main_b3];
  const combat = condition.combat_settings;
  $("#scope-boss").textContent = `DEF ${combat.boss_def} · ${combat.boss_element || "속성 미지정"}`;
  const thresholds = condition.thresholds;
  $("#scope-combat").textContent = `${baselineLabel} 기준 · ${combat.duration_sec}초 · 코어 ${combat.core_hit_rate_pct}% · 적정거리 ${combat.range_bonus_pct}% · 동률 ±${thresholds.tie_band_pct}% · 명확 ${thresholds.clear_advantage_pct}%`;
  const signature = condition.mechanics_signature;
  $("#batch-revision").textContent = `${signature.engine_rule_revision} · ${signature.skill_hook_revision}`;
  $("#b1-definitions").replaceChildren(...batch.checkpoint_definitions.b1.map((profile) => {
    const item = document.createElement("li");
    const ol = profile.overload;
    item.textContent = `${profile.label}: ${profile.gear.toUpperCase()}, 공${ol.atk_lines}·우${ol.element_lines}·장${ol.ammo_lines}, 수집품 ${profile.collection === "none" ? "없음" : profile.collection}`;
    return item;
  }));
  $("#dealer-definitions").replaceChildren(...batch.checkpoint_definitions.dealer.map((profile) => {
    const item = document.createElement("li");
    item.textContent = `${profile.label}`;
    return item;
  }));

  const extremeDefinitions = [
    ["몰아주기 최대", extremes.most_funnel_favorable],
    [`${baselineLabel} 최대`, extremes.most_conventional_favorable],
    ["손익분기 최근접", extremes.closest_to_break_even],
  ];
  $("#extreme-cases").replaceChildren(...extremeDefinitions.map(([label, item]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "extreme-case";
    if (!item) {
      button.disabled = true;
      button.innerHTML = `<span>${label}</span><strong>계산 불가</strong>`;
      return button;
    }
    button.innerHTML = `<span>${label}</span><strong>${caseLabel(item)}</strong><div><b>${signedPercent(item.relative_change)}</b><small>Main ${formatPercent(item.conventional_main_share)} · 분기 ${formatPercent(item.break_even_main_share_c)} · 간극 ${percentagePoint(item.margin)}</small></div>`;
    button.addEventListener("click", () => selectBatchResult(batch.results.find((result) => result.case_id === item.case_id)));
    return button;
  }));
}

function renderGroupRows(selector, groups) {
  $(selector).replaceChildren(...groups.map((group) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${group.label}</td><td class="${group.relative_change.average > 0 ? "positive" : group.relative_change.average < 0 ? "negative" : ""}">${signedPercent(group.relative_change.average)}</td><td>${percentRange(group.relative_change, true)}</td><td>${formatPercent(group.conventional_main_share.average)}</td><td>${group.conventional_wins}/${group.funnel_wins}/${group.tie_band}</td>`;
    return row;
  }));
}

function renderCrossTable(batch) {
  const b1Profiles = batch.checkpoint_definitions.b1;
  const dealerProfiles = batch.checkpoint_definitions.dealer;
  const header = document.createElement("tr");
  header.innerHTML = `<th>딜러 기준점</th>${b1Profiles.map((profile) => `<th>${profile.label}</th>`).join("")}`;
  $("#cross-table-head").replaceChildren(header);
  $("#cross-table-body").replaceChildren(...dealerProfiles.map((dealer) => {
    const row = document.createElement("tr");
    const cells = b1Profiles.map((b1) => batch.results.find((item) => item.labels.b1_profile === b1.id && item.labels.dealer_profile === dealer.id));
    row.innerHTML = `<td>${dealer.label}</td>${cells.map((item) => `<td class="${item.summary.relative_change > 0 ? "positive" : item.summary.relative_change < 0 ? "negative" : ""}">${signedPercent(item.summary.relative_change)}<small>Main ${formatPercent(item.summary.conventional_main_share)}</small></td>`).join("")}`;
    return row;
  }));
}

function renderCharacterAggregate(batch) {
  $("#character-aggregate-body").replaceChildren(...Object.entries(batch.aggregate.character_shares).map(([actor, shares]) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${batch.display_names[actor]}</td><td>${formatPercent(shares.conventional.average)}</td><td>${percentRange(shares.conventional)}</td><td>${formatPercent(shares.funnel.average)}</td><td>${percentRange(shares.funnel)}</td>`;
    return row;
  }));
}

function renderScatter(results) {
  const plot = $("#scatter-plot");
  plot.replaceChildren();
  const xValues = results.map((result) => (result.summary.conventional_main_share || 0) * 100);
  const xMin = Math.max(0, Math.floor((Math.min(...xValues) - 5) / 5) * 5);
  const xMax = Math.min(100, Math.ceil((Math.max(...xValues) + 5) / 5) * 5);
  const xSpan = Math.max(5, xMax - xMin);
  const maxAbs = Math.max(0.02, ...results.map((result) => Math.abs(result.summary.relative_change || 0))) * 1.2;
  for (const ratio of [0, 0.25, 0.5, 0.75, 1]) {
    const x = xMin + xSpan * ratio;
    const line = document.createElement("i");
    line.className = "grid-line x";
    line.style.left = `${ratio * 100}%`;
    const label = document.createElement("span");
    label.className = "grid-label x";
    label.style.left = `${ratio * 100}%`;
    label.textContent = `${x.toFixed(x % 1 ? 1 : 0)}%`;
    plot.append(line, label);
  }
  for (const ratio of [-1, -0.5, 0, 0.5, 1]) {
    const top = 50 - ratio * 45;
    const line = document.createElement("i");
    line.className = `grid-line y${ratio === 0 ? " zero" : ""}`;
    line.style.top = `${top}%`;
    const label = document.createElement("span");
    label.className = "grid-label y";
    label.style.top = `${top}%`;
    label.textContent = `${ratio >= 0 ? "+" : ""}${(ratio * maxAbs * 100).toFixed(1)}%`;
    plot.append(line, label);
  }
  results.forEach((result) => {
    const summary = result.summary;
    const point = document.createElement("button");
    point.type = "button";
    point.className = `sample-point ${result.labels.b1_profile} ${pointShape(result.labels.dealer_profile)}`;
    point.dataset.caseId = result.case_id;
    point.style.left = `${(((summary.conventional_main_share || 0) * 100 - xMin) / xSpan) * 100}%`;
    point.style.top = `${50 - ((summary.relative_change || 0) / maxAbs) * 45}%`;
    point.title = `${result.labels.b1_label}\n${result.labels.dealer_label}\nMain ${formatPercent(summary.conventional_main_share)} / 증감 ${signedPercent(summary.relative_change)}`;
    point.setAttribute("aria-label", point.title.replaceAll("\n", ", "));
    point.addEventListener("click", () => selectBatchResult(result));
    plot.append(point);
  });
}

function renderBatch(batch) {
  state.batch = batch;
  const results = batch.results;
  const first = results[0];
  const mainName = batch.display_names[first.summary.main_actor];
  const secondaryName = batch.display_names[first.summary.secondary_b3];
  applyBaselineText(batch.baseline_label);
  $("#batch-title").textContent = `${mainName} / ${secondaryName} 기준점 지도`;
  $("#batch-count").textContent = results.length;
  $("#batch-c-count").textContent = results.filter((item) => item.summary.outcome_band.includes("conventional")).length;
  $("#batch-f-count").textContent = results.filter((item) => item.summary.outcome_band.includes("funnel")).length;
  $("#batch-tie-count").textContent = results.filter((item) => item.summary.outcome_band === "tie_band").length;
  renderAggregate(batch);
  renderScatter(results);
  renderCrossTable(batch);
  renderGroupRows("#b1-group-body", batch.aggregate.by_b1_profile);
  renderGroupRows("#dealer-group-body", batch.aggregate.by_dealer_profile);
  renderCharacterAggregate(batch);
  $("#batch-table-body").replaceChildren(...results.map((result) => {
    const summary = result.summary;
    const row = document.createElement("tr");
    row.dataset.caseId = result.case_id;
    row.innerHTML = `<td>${result.labels.b1_label}</td><td>${result.labels.dealer_label}</td><td>${formatDamage(summary.conventional_damage)}</td><td>${formatDamage(summary.funnel_damage)}</td><td>${formatPercent(summary.conventional_main_share)}</td><td class="${summary.relative_change > 0 ? "positive" : summary.relative_change < 0 ? "negative" : ""}">${signedPercent(summary.relative_change)}</td><td>${formatPercent(summary.break_even_main_share_c)}</td><td>${percentagePoint(summary.margin)}</td><td>${outcomeLabel(summary.outcome_band, batch.baseline_label)}</td>`;
    row.addEventListener("click", () => selectBatchResult(result));
    return row;
  }));
  selectBatchResult(first);
  $("#batch-results").hidden = false;
}

async function calculate() {
  const button = $("#calculate-button");
  button.disabled = true;
  $("#results").hidden = true;
  $("#batch-results").hidden = true;
  $("#error-state").hidden = true;
  $("#loading-state").hidden = false;
  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectPayload()),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
    renderReport(payload);
  } catch (error) {
    $("#error-message").textContent = error.message;
    $("#error-state").hidden = false;
  } finally {
    $("#loading-state").hidden = true;
    button.disabled = false;
  }
}

async function calculateBatch() {
  const batchButton = $("#batch-button");
  const calculateButton = $("#calculate-button");
  batchButton.disabled = true;
  calculateButton.disabled = true;
  $("#results").hidden = true;
  $("#batch-results").hidden = true;
  $("#error-state").hidden = true;
  $("#loading-state").hidden = false;
  $("#loading-state p").textContent = "12개 기준점을 순서대로 계산하고 있습니다.";
  try {
    const response = await fetch("/api/checkpoints", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(batchRequestPayload()),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
    renderBatch(payload);
  } catch (error) {
    $("#error-message").textContent = error.message;
    $("#error-state").hidden = false;
  } finally {
    $("#loading-state").hidden = true;
    $("#loading-state p").textContent = "14버스트 RAID14 구간을 계산하고 있습니다.";
    batchButton.disabled = false;
    calculateButton.disabled = false;
  }
}

function canvasBlob(canvas) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error("PNG 데이터를 만들지 못했습니다."));
    }, "image/png");
  });
}

async function exportBatchPng() {
  if (!state.batch) return;
  const button = $("#batch-png-button");
  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = "PNG 생성 중";
  try {
    await document.fonts.ready;
    const source = $("#batch-results");
    const width = Math.ceil(Math.max(source.clientWidth, source.scrollWidth));
    const height = Math.ceil(source.scrollHeight);
    const scale = Math.min(2, Math.sqrt(28_000_000 / (width * height)));
    if (typeof window.html2canvas !== "function") {
      throw new Error("PNG 렌더러를 불러오지 못했습니다.");
    }
    const canvas = await window.html2canvas(source, {
      backgroundColor: "#f3f5f6",
      scale,
      width,
      height,
      windowWidth: Math.max(document.documentElement.clientWidth, width),
      logging: false,
      onclone: (clonedDocument) => {
        const clonedReport = clonedDocument.querySelector("#batch-results");
        clonedReport.querySelectorAll(".export-exclude").forEach((item) => item.remove());
        clonedReport.querySelectorAll(".table-wrap").forEach((item) => { item.style.overflow = "visible"; });
      },
    });
    const png = await canvasBlob(canvas);
    const pngUrl = URL.createObjectURL(png);
    const link = document.createElement("a");
    link.href = pngUrl;
    link.download = `crown-mast-comparison-${fileDate()}.png`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(pngUrl), 1000);
  } catch (error) {
    $("#error-message").textContent = `PNG 저장 실패: ${error.message}`;
    $("#error-state").hidden = false;
  } finally {
    button.disabled = false;
    button.textContent = originalLabel;
  }
}

function setupTabs() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab-button").forEach((item) => {
        const active = item === button;
        item.classList.toggle("active", active);
        item.setAttribute("aria-selected", String(active));
      });
      $("#characters-tab").hidden = button.dataset.tab !== "characters";
      $("#cycles-tab").hidden = button.dataset.tab !== "cycles";
    });
  });
}

async function initialize() {
  const response = await fetch("/api/meta");
  if (!response.ok) throw new Error("엔진 메타데이터를 불러오지 못했습니다.");
  state.metadata = await response.json();
  $("#baseline-options").replaceChildren(...state.metadata.baseline_rotations.map((rotation) => {
    const label = document.createElement("label");
    label.title = rotation.sequence;
    label.innerHTML = `<input type="radio" name="baseline-rotation" value="${rotation.id}"><span>${rotation.label}</span>`;
    return label;
  }));
  fillSelect($("#b1-select"), state.metadata.b1_options);
  fillSelect($("#main-b3-select"), state.metadata.b3_options);
  fillSelect($("#secondary-b3-select"), state.metadata.b3_options);
  state.metadata.boss_elements.forEach((element) => {
    const option = document.createElement("option");
    option.value = element;
    option.textContent = element;
    $("#boss-element").append(option);
  });
  $("#revision-label").textContent = state.metadata.revisions.engine_rule;
  setDefaults();
  if (new URLSearchParams(window.location.search).get("mode") === "batch") {
    await calculateBatch();
  } else {
    await calculate();
  }
}

form.addEventListener("submit", (event) => { event.preventDefault(); calculate(); });
$("#b1-select").addEventListener("change", renderBuildRows);
$("#main-b3-select").addEventListener("change", (event) => syncB3Options(event.target));
$("#secondary-b3-select").addEventListener("change", (event) => syncB3Options(event.target));
$("#reset-button").addEventListener("click", () => { setDefaults(); calculate(); });
$("#batch-button").addEventListener("click", calculateBatch);
$("#batch-png-button").addEventListener("click", exportBatchPng);
$("#download-button").addEventListener("click", () => {
  if (!state.report) return;
  const blob = new Blob([JSON.stringify(state.report, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `crown-mast-report-${fileDate()}.json`;
  link.click();
  URL.revokeObjectURL(link.href);
});
$("#batch-download-button").addEventListener("click", () => {
  if (!state.batch) return;
  const blob = new Blob([JSON.stringify(state.batch, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `crown-mast-checkpoints-${fileDate()}.json`;
  link.click();
  URL.revokeObjectURL(link.href);
});
setupTabs();
initialize().catch((error) => {
  $("#loading-state").hidden = true;
  $("#error-message").textContent = error.message;
  $("#error-state").hidden = false;
});
