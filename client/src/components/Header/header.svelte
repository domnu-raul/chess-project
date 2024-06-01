<script lang="ts">
	import { onMount } from 'svelte';
	import useFetch from '$lib/useFetch';
	import { token } from '$lib/store';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';

	let username;
	let loggedIn = false;

	function getUser() {
		useFetch('http://localhost:8000/user/me', {
			method: 'GET'
		})
			.then((res) => {
				username = res['username'];
				loggedIn = true;
			})
			.catch((err) => {
				username = null;
				loggedIn = false;
			});
	}

	function logout() {
		if (browser) {
			token.set(null);
			loggedIn = false;
		}
	}

	token.subscribe((value) => {
		if (value) {
			getUser();
		}
	});
</script>

<div
	class="flex flex-row justify-between gap-4 from-zinc-900 from-20% to-transparent to-50% bg-gradient-to-br h-24 w-screen"
>
	<a href="/" class="p-2">
		<h1 class="text-3xl font-medium text-stone-100">Chess</h1>
	</a>

	<div
		id="nav"
		class="flex flex-row flex-row-reverse from-zinc-900 from-20% to-transparent to-50% bg-gradient-to-bl h-full w-full p-2"
	>
		{#if loggedIn}
			<div class="flex flex-row gap-4">
				<a href="/me" class="text-stone-100 hover:underline hover:underline-offset-4">{username}</a>
				<a
					href=""
					on:click={logout}
					class="text-stone-100 hover:underline hover:underline-offset-4"
				>
					Log out
				</a>
			</div>
		{/if}
	</div>
</div>
