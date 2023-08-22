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
                <td id=id>{item.job_id}</td>
                <td id=cmd>{item.cmd}</td>
                <td id=status>{item.status}</td>
                <td id=capture>{item.capture_stdout === 1 ? '✓' : "✗"}</td>
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
        background-color: orangered;
    }

    tr[value="running"] {
        background-color: yellow;
    }

    tr[value="starting"] {
        background-color: aqua;
    }

    #id {
        width: 5%;
    }

    #cmd {
        width: 80%;
        text-align: left;
        padding-left: 5px;
    }

    #status {
        width: 10%;
    }

    #capture {
        width: 5%;
    }
</style>