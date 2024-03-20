<script>
	let board = [
		['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
		['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
		['', '', '', '', '', '', '', ''],
		['', '', '', '', '', '', '', ''],
		['', '', '', '', '', '', '', ''],
		['', '', '', '', '', '', '', ''],
		['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
		['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
	];
</script>

<div class="grid grid-rows-8 grid-cols-8 w-[600px] h-[600px]">
	{#each board as row, i}
		{#each row as square, j}
        <div class={i + j % 2 == 0 ? "bg-slate-300" : "bg-green-800"}>
            <img src={`%sveltekit.assets%/pieces/${square}.png`} alt="">

        </div>

        {/each}
	{/each}
</div>
