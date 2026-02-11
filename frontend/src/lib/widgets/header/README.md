# Header

Шапка приложения с логотипом, сменой темы (светлая/тёмная) и местом для дополнительных кнопок.

## Тема

- Тема сохраняется в `localStorage` (`theme`: `light` | `dark`).
- При первом визите используется системная настройка `prefers-color-scheme`.
- В `app.html` скрипт задаёт класс на `<html>` до первой отрисовки, чтобы не было мигания.

## Добавление кнопок

Передайте слот `actions` с разметкой кнопок (они появятся слева от «Настройки» и «Тема»):

```svelte
<Header>
  {#snippet actions()}
    <button type="button" class="header-action" onclick={...}>
      <!-- иконка или текст -->
    </button>
  {/snippet}
</Header>
```

Для единого вида кнопок используйте те же классы:  
`p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-900`
