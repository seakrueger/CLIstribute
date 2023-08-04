<script>
    import { submit } from "../api/api.js"

    let cmd = '';
    let capture = false;
    let response = '';

    async function handleSubmit() {
        const data = {
            cmd: cmd,
            capture: capture,
        };

        response = submit(JSON.stringify(data))
    }
</script>
 
<div class="command-form">
    <form on:submit|preventDefault={handleSubmit}>
        <label>
            Command:
            <input type="text" bind:value={cmd} />
        </label>
        <label>
            Capture Output:
            <input type="checkbox" bind:checked={capture} />
        </label>
        <button type="submit">Submit</button>
    </form>
</div>

<style>
    form {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2rem;
        background-color: #f8f8f8;
        padding: 1rem;
        border-top: 1px solid #ccc;
    }

    label {
        display: flex;
        flex-direction: row;
        align-items: center;
    }

    input {
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #ccc;
    }

    button {
        padding: 8px 16px;
        background-color: #ff3e00;
        color: white;
        border: none;
        cursor: pointer;
        border-radius: 4px;
        margin-left: 0.5rem;
    }
</style>
