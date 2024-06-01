<script lang="ts">
	import { token } from '$lib/store';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';

	let token_value;
	token.subscribe((value) => {
		token_value = value;
	});

	$: if (!$token) {
		if (browser) {
			goto('/login', { replaceState: true });
		}
	}
</script>

<slot />
<h1>{token_value}</h1>
