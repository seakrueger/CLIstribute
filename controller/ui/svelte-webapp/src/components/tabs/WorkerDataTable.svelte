<script>
    import { onDestroy } from "svelte";
    import { getWorkers } from "../../api/api";

    let data = {};

    async function fetchData() {
        data = await getWorkers()
    }

    fetchData();

    let interval;
    $: {
        clearInterval(interval);
        interval = setInterval(fetchData, 2500);
    }

    onDestroy(() => {
        clearInterval(interval);
    });
</script>

<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Status</th>
            <th>Current Job ID</th>
            <th>IP</th>
        </tr>
    </thead>
    <tbody>
        {#each data as item}
            <tr value={item.status}>
                <td>{item.worker_id}</td>
                <td>{item.name}</td>
                <td>{item.status}</td>
                <td>{item.current_job_id}</td>
                <td>{item.ip}</td>
            </tr>        
        {/each}
    </tbody>
</table>

<style>
    table, th, td {
        border: 1px solid;
    }

    table {
        flex: 1;
        width: 100%;
        margin-bottom: 5rem;
    }

    tr[value="accepting-work"] {
        background-color: #80ff0052;
    }

    tr[value="not-accepting-work"] {
        background-color: #ff2f0052;
    }

    tr[value="offline"] {
        background-color: #c0b6b67b;
    }
</style>