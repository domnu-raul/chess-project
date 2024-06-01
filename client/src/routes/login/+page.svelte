<script>
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { token } from '$lib/store';
	import useFetch from '$lib/useFetch';
	let username = '';
	let password = '';

	if (browser) {
		if (localStorage.getItem('token')) goto('/', { replaceState: true });
	}

	async function login(event) {
		event.preventDefault();
		const encoded = new FormData();
		encoded.set('username', username);
		encoded.set('password', password);

		const encodedData = new URLSearchParams();
		encodedData.append('username', username);
		encodedData.append('password', password);

		const res = await fetch('http://localhost:8000/auth/login', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			body: encodedData
		});

		if (res.ok) {
			const data = await res.json();

			token.set(data['token_type'] + ' ' + data['access_token']);
			if (browser) goto('/');
		}
	}
</script>

<form
	on:submit={login}
	class="flex flex-col gap-4 p-6 justify-between bg-zinc-800 b-2 border-slate-300 border-solid border-2
	rounded-sm w-fit"
>
	<input
		type="text"
		bind:value={username}
		placeholder="Username"
		name="username"
		class="h-10 border-slate-500 focus:border-slate-700 focus:border-solid focus:border-2 border-solid border-2 p-2 rounded-sm"
	/>
	<input
		type="password"
		bind:value={password}
		placeholder="Password"
		name="password"
		class="h-10 border-slate-500 focus:border-slate-700 focus:border-solid focus:border-2 border-solid border-2 p-2 rounded-sm mb-2"
	/>
	<button
		type="submit"
		class="h-10 border-slate-500 focus:border-slate-700 focus:border-solid focus:border-2 border-solid border-2 p-2 rounded-sm text-sky-100 bg-emerald-600 hover:bg-emerald-700 font-medium transition-colors"
		>Login</button
	>
</form>
