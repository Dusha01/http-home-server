<script lang="ts">
	interface Props {
		type?: string;
		value?: string;
		placeholder?: string;
		disabled?: boolean;
		class?: string;
		name?: string;
		autocomplete?: string;
		oninput?: (e: Event) => void;
	}
	let {
		type = 'text',
		value = $bindable(''),
		placeholder = '',
		disabled = false,
		class: className = '',
		name,
		autocomplete,
		oninput
	}: Props = $props();
</script>

<input
	{type}
	{value}
	{placeholder}
	{disabled}
	{name}
	{autocomplete}
	class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-800 shadow-sm focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500 disabled:bg-slate-100 {className}"
	oninput={(e) => {
		value = (e.currentTarget as HTMLInputElement).value;
		oninput?.(e);
	}}
/>
