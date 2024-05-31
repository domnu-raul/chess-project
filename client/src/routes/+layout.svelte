<script>
	import '../app.css';
	import Header from '../components/Header/header.svelte';
</script>

<div id="app" class="flex flex-col items-center">
	<Header></Header>
	<slot />
</div>

<style>
	#app {
		--first-color: #18181b;
		--second-color: #27272a;
		width: 100vw;
		height: 100vh;
		background: conic-gradient(
			var(--first-color) 90deg,
			var(--second-color) 90deg 180deg,
			var(--first-color) 180deg 270deg,
			var(--second-color) 270deg
		);
		background-repeat: repeat;
		background-size: 140px 140px;
		background-position: 0 0;
	}
</style>
