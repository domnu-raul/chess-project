<script>
	let username = '';
	let password = '';

	async function handleSubmit() {
		console.log('Username:', username);
	}
</script>

<div>
	<form
		method="post"
		action="http://localhost:8000/auth/login"
		class="flex flex-col gap-2 p-6 bg-slate-800 b-2 border-sky-50 rounded-sm w-fit"
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
			class="h-10 border-slate-500 focus:border-slate-700 focus:border-solid focus:border-2 border-solid border-2 p-2 rounded-sm"
		/>
		<button
			type="submit"
			class="h-10 border-slate-500 focus:border-slate-700 focus:border-solid focus:border-2 border-solid border-2 p-2 rounded-sm text-sky-100 bg-emerald-600 hover:bg-emerald-700 font-medium transition-colors"
			>Login</button
		>
	</form>
</div>
