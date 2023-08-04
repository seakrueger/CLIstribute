<script>
    import CommandDataTable from './CommandDataTable.svelte';
    import WorkerDataTable from './WorkerDataTable.svelte';
</script>

<div class="tabs">
    <input class="input" name="tabs" type="radio" id="tab-1" checked="checked"/>
    <label class="label" for="tab-1">Commands</label>
    <div class="panel">
        <CommandDataTable />
    </div>
    <input class="input" name="tabs" type="radio" id="tab-2"/>
    <label class="label" for="tab-2">Workers</label>
    <div class="panel">
        <WorkerDataTable />
    </div>
    <input class="input" name="tabs" type="radio" id="tab-3"/>
    <label class="label" for="tab-3">Logs</label>
    <div class="panel">
    </div>
</div>

<style>
    * {
        box-sizing: border-box;
    }

    .tabs {
        display: flex;
        flex-wrap: wrap;
        background: #e5e5e5;
    }

    .input {
        position: absolute;
        opacity: 0;
    }

    .label {
        width: 100%;
        padding: 20px 30px;
        background: #e5e5e5;
        cursor: pointer;
        font-weight: bold;
        font-size: 18px;
        color: #7f7f7f;
        transition: background 0.1s, color 0.1s;
    }
    
    .label:hover {
        background: #d8d8d8;
    }

    .label:active {
        background: #ccc;
    }

    .input:focus + .label {
        z-index: 1;
    }

    .input:checked + .label {
        background: #fff;
        color: #000;
    }

    @media (min-width: 600px) {
        .label {
            width: auto;
        }
    }

    .panel {
        display: none;
        padding: 20px 30px 30px;
        width: 100%;
        background: #fff;
    }

    @media (min-width: 600px) {
        .panel {
            order: 99;
        }
    }

    .input:checked + .label + .panel {
        display: block;
    }
</style>
