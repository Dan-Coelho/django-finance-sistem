# 6. Design System

O Design System do Finanpy garante uma experiência de usuário coesa e moderna. Ele é baseado em um tema escuro e utiliza TailwindCSS.

## Paleta de Cores

### Cores Primárias:
- **Primary:** `#6366f1` (Indigo-500)
- **Secondary:** `#8b5cf6` (Violet-500)
- **Accent:** `#06b6d4` (Cyan-500)

### Cores de Fundo:
- **Background Primary:** `#0f172a` (Slate-900)
- **Background Secondary:** `#1e293b` (Slate-800)

### Cores de Texto:
- **Text Primary:** `#f1f5f9` (Slate-100)
- **Text Secondary:** `#cbd5e1` (Slate-300)

### Cores de Status:
- **Success:** `#10b981` (Emerald-500)
- **Warning:** `#f59e0b` (Amber-500)
- **Error:** `#ef4444` (Red-500)
- **Info:** `#3b82f6` (Blue-500)

## Tipografia

- **Fonte:** 'Inter', system-ui, sans-serif
- **Tamanhos Base:**
  - `sm`: 0.875rem (14px)
  - `base`: 1rem (16px)
  - `lg`: 1.125rem (18px)
  - `xl`: 1.25rem (20px)

## Componentes

Os componentes são construídos utilizando classes do TailwindCSS diretamente nos templates Django.

### Botões
```html
<!-- Botão Primário -->
<button class="px-6 py-3 bg-gradient-to-r from-indigo-500 to-violet-500 text-white rounded-lg font-semibold hover:from-indigo-600 hover:to-violet-600">
  Texto do Botão
</button>

<!-- Botão Secundário -->
<button class="px-6 py-3 bg-slate-700 text-slate-100 rounded-lg font-semibold hover:bg-slate-600">
  Texto do Botão
</button>
```

### Inputs
```html
<label class="block text-sm font-semibold text-slate-300">Nome do Campo</label>
<input type="text" class="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500">
```

### Cards
```html
<div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
  <h3 class="text-xl font-bold text-slate-100 mb-2">Título do Card</h3>
  <p class="text-slate-300">Conteúdo do card</p>
</div>
```
