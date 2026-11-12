const state = {
  items: [],
  query: "",
  provider: "azure",
  category: "all",
  selected: null,
};

const grid = document.querySelector("#grid");
const cats = document.querySelector("#cats");
const search = document.querySelector("#search");
const count = document.querySelector("#count");
const detail = document.querySelector("#detail");
const providers = document.querySelectorAll(".provider");

const WORDS = { ai: "AI", iot: "IoT", devops: "DevOps" };

function providerOf(item) {
  return item.provider || "azure";
}

function categoryLabel(module) {
  return module.split("_").map((part) => WORDS[part] || part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
}

function haystack(item) {
  return [item.provider, item.module, item.name, item.service, ...(item.aliases || [])].join(" ").toLowerCase();
}

function inProvider(item) {
  return providerOf(item) === state.provider;
}

function visible() {
  const words = state.query.toLowerCase().split(/\s+/).filter(Boolean);
  return state.items.filter((item) => {
    if (!inProvider(item)) return false;
    if (state.category !== "all" && item.module !== state.category) return false;
    return words.every((word) => haystack(item).includes(word));
  });
}

function renderCategories() {
  const counts = new Map();
  for (const item of state.items) {
    if (inProvider(item)) counts.set(item.module, (counts.get(item.module) || 0) + 1);
  }
  const names = [...counts.keys()].sort((a, b) => categoryLabel(a).localeCompare(categoryLabel(b)));
  const total = [...counts.values()].reduce((sum, value) => sum + value, 0);
  const entries = [["all", "All", total], ...names.map((name) => [name, categoryLabel(name), counts.get(name)])];
  cats.replaceChildren(...entries.map(([id, label, total]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "cat";
    button.dataset.category = id;
    button.setAttribute("aria-pressed", String(id === state.category));
    button.innerHTML = `${label} <span>${total}</span>`;
    button.addEventListener("click", () => {
      state.category = id;
      syncQuery();
      render();
    });
    return button;
  }));
}

function card(item) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "card";
  button.setAttribute("aria-pressed", String(state.selected === item));
  const image = document.createElement("img");
  image.src = item.icon;
  image.alt = "";
  image.width = 48;
  image.height = 48;
  image.loading = "lazy";
  const service = document.createElement("span");
  service.className = "service";
  service.textContent = item.service;
  const klass = document.createElement("span");
  klass.className = "klass";
  klass.textContent = item.aliases?.[0] || item.name;
  button.append(image, service, klass);
  button.addEventListener("click", () => {
    state.selected = item;
    render();
    detail.scrollIntoView({ block: "nearest" });
  });
  return button;
}

function copyButton(text) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "copy";
  button.textContent = "Copy";
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      return;
    }
    button.textContent = "Copied";
    setTimeout(() => { button.textContent = "Copy"; }, 1200);
  });
  return button;
}

function renderDetail() {
  const item = state.selected;
  detail.replaceChildren();
  detail.classList.toggle("is-open", Boolean(item));
  if (!item) {
    detail.innerHTML = "<p class=\"muted\">Choose an icon to see the class name and the import to paste into a diagram.</p>";
    return;
  }
  const preview = document.createElement("div");
  preview.className = "preview";
  const image = document.createElement("img");
  image.src = item.icon;
  image.alt = item.service;
  image.width = 72;
  image.height = 72;
  preview.append(image);

  const title = document.createElement("h2");
  title.textContent = item.service;
  const meta = document.createElement("p");
  meta.className = "muted";
  meta.textContent = `${providerOf(item)} · ${item.module}.${item.name}`;
  detail.append(preview, title, meta);

  if (item.aliases?.length) {
    const aliases = document.createElement("div");
    aliases.className = "aliases";
    for (const alias of item.aliases) {
      const chip = document.createElement("span");
      chip.className = "alias";
      chip.textContent = alias;
      aliases.append(chip);
    }
    detail.append(aliases);
  }

  for (const line of item.imports) {
    const row = document.createElement("div");
    row.className = "import";
    const code = document.createElement("code");
    code.textContent = line;
    row.append(code, copyButton(line));
    detail.append(row);
  }
}

function render() {
  const items = visible();
  const labels = { azure: "Azure", aws: "AWS", external: "External" };
  const cloud = labels[state.provider] || state.provider;
  count.textContent = `${items.length} ${cloud} icon${items.length === 1 ? "" : "s"}`;
  for (const button of providers) {
    button.setAttribute("aria-pressed", String(button.dataset.provider === state.provider));
  }
  for (const button of cats.querySelectorAll(".cat")) {
    button.setAttribute("aria-pressed", String(button.dataset.category === state.category));
  }
  if (!items.length) {
    grid.replaceChildren();
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No icon matches that search.";
    grid.append(empty);
  } else {
    grid.replaceChildren(...items.map(card));
  }
  renderDetail();
}

function syncQuery() {
  const params = new URLSearchParams();
  if (state.provider !== "azure") params.set("provider", state.provider);
  if (state.query) params.set("q", state.query);
  if (state.category !== "all") params.set("category", state.category);
  const next = params.toString();
  history.replaceState(null, "", next ? `?${next}` : location.pathname);
}

for (const button of providers) {
  button.addEventListener("click", () => {
    state.provider = button.dataset.provider;
    state.category = "all";
    state.selected = null;
    syncQuery();
    renderCategories();
    render();
  });
}

search.addEventListener("input", () => {
  state.query = search.value;
  syncQuery();
  render();
});

const params = new URLSearchParams(location.search);
state.query = params.get("q") || "";
state.provider = ["aws", "external"].includes(params.get("provider")) ? params.get("provider") : "azure";
state.category = (params.get("category") || "all").split("/").pop();
search.value = state.query;

const response = await fetch("catalog.json");
state.items = await response.json();
state.items.sort((a, b) => a.service.localeCompare(b.service) || a.name.localeCompare(b.name));
renderCategories();
render();
