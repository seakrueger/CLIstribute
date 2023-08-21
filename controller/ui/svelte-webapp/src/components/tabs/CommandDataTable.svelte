<script>
    import { getCommands } from "../../api/api";

    let data = {};

    async function fetchData() {
        data = await getCommands()
    }

    fetchData();

    let interval;
    $: {
        clearInterval(interval);
        interval = setInterval(fetchData, 2500);
    }
</script>

<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Command</th>
            <th>Status</th>
            <th>Capture Output</th>
        </tr>
    </thead>
    <tbody>
        {#each data as item}
            <tr value={item.status}>
                <td>{item.job_id}</td>
                <td>{item.cmd}</td>
                <td>{item.status}</td>
                <td>{item.capture_stdout}</td>
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

    tr[value="successful"] {
        background-color: chartreuse;
    }

    tr[value="failed"] {
        background-color: firebrick;
    }

    tr[value="running"] {
        background-color: yellow;
    }

    tr[value="starting"] {
        background-color: aqua;
    }
</style>