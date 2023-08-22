<script>
    import { onDestroy } from "svelte";
    import { getLogs } from "../../api/api";

    let streamData = {};

    async function fetchStreams() {
        streamData = await getLogs();
    }

    fetchStreams();

    let interval;
    $: {
        clearInterval(interval);
        interval = setInterval(fetchStreams, 1000);
    }

    onDestroy(() => {
        clearInterval(interval);
    });
</script>

<h2>Live output from workers</h2>
<div class="grid-container">
    {#each Object.keys(streamData) as source}
        <div class="stream-box">
            <h3>Worker {source}</h3>
            <pre>{streamData[source].join("")}</pre>
        </div>
    {/each}
</div>

<style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
        gap: 10px;
        padding-top: 20px;
    }

    .stream-box {
        width: 600px;
        border: 1px solid #dee2e6;
        background-color: #f5f3f3;
        margin: 10px;
        padding: 5px;
        overflow: hidden;
    }

    .stream-box pre {
        text-align: left;
        font-family: monospace;
        font-size: 12px;
        white-space: pre-wrap;
        word-wrap: break-word;
        width: 100%;
        max-width: 100%;
        max-height: 100%;
    }
</style>