<script>
  import Input from './components/Input.svelte'
  import Tabs from './components/Tabs.svelte';
</script>

<main>
  <Tabs />
  <Input />
</main>

<style>
  main {
	text-align: center;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
  }
</style>
 