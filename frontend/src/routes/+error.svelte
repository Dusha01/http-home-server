<script lang="ts">
    import { page } from '$app/stores';
    import { ErrorPage, NotFoundPage} from "$lib";
</script>


{#if $page.status === 404}
    <NotFoundPage statusError="404" titleError="Страница не найдена" />
{:else}
    <ErrorPage status={$page.status} error={$page.error} />
{/if}