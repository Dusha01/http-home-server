<script lang="ts">
	interface Props {
		type?: 'button' | 'submit';
		disabled?: boolean;
		class?: string;
		children?: import('svelte').Snippet;
	}
	let { type = 'button', disabled = false, class: className = '', children }: Props = $props();
</script>

<button
	{type}
	{disabled}
	class="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white shadow hover:bg-sky-700 disabled:opacity-50 {className}"
>
	{#if children}{@render children?.()}{/if}
</button>
