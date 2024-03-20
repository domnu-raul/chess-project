<script>
	import { onMount } from 'svelte';

	let board = new Array();
	let game_key;
	let current_fen;
	let move_tree;
	let current_move = null;

	onMount(async () => {
		fetch('http://localhost:8000/start', {
			method: 'POST'
		})
			.then((response) => response.json())
			.then((obj) => {
				game_key = obj.key;
				current_fen = obj.fen;
				board = getBoard(current_fen);
			});
	});

	function getBoard(fen) {
		let board = new Array(8);
		for (let i = 0; i < 8; i++) board[i] = new Array(8);

		let rows = fen.split('/');

		let i = 0;
		for (let row of rows) {
			let j = 0;
			for (let c of row) {
				let n = Number.parseInt(c);
				if (Number.isInteger(n)) {
					let new_j = j + n;
					for (let k = j; k < new_j; k++) board[i][k] = '';
					j = new_j;
				} else {
					board[i][j] = c;
					j++;
				}
			}
			i++;
		}

		updateMoveTree();
		return board;
	}

	function getPosition(x, y) {
		let char = String.fromCharCode(97 + y);
		let int = Math.abs(x - 8);
		return `${char}${int}`;
	}

	function updateMoveTree() {
		fetch(`http://localhost:8000/${game_key}`)
			.then((response) => response.json())
			.then((response) => (move_tree = response));
	}

	function commitMove(start, end) {
		fetch(`http://localhost:8000/${game_key}/${start}${end}`, {
			method: 'PUT'
		})
			.then((response) => response.json())
			.then((response) => {
				current_fen = response['fen'];
				board = getBoard(current_fen);
			});
	}

	function move(x, y) {
		let pos = getPosition(x, y);
		if (current_move == null) {
			let sugested = move_tree[pos];
			if (sugested == undefined) return;

			current_move = pos;
		} else {
			if (move_tree[current_move].some((str) => str == pos)) {
				commitMove(current_move, pos);
			}
			current_move = null;
		}
	}
</script>

<div bind:this={move_tree} class="grid grid-rows-8 grid-cols-8 w-[600px] h-[600px]">
	{#each board as row, x}
		{#each row as square, y}
			<button
				on:click={() => move(x, y)}
				class={`
				${(x + y) % 2 == 0 ? 'bg-slate-300' : 'bg-green-800'} flex flex-row`}
				id={`square-${getPosition(x, y)}`}
			>
				{#if x == 7}
					<span
						class={`z-[1] m-[1px] text-sm font-medium ${(x + y) % 2 == 0 ? 'text-slate-700' : 'text-slate-200'} absolute self-end`}
						>{`${String.fromCharCode(65 + y)}`}</span
					>
				{/if}
				{#if y == 0}
					<span
						class={`z-[1] m-[1px] text-sm font-medium ${(x + y) % 2 == 0 ? 'text-slate-700' : 'text-slate-200'} absolute`}
						>{Math.abs(x - 8)}</span
					>
				{/if}

				{#if square !== ''}
					<img src={`pieces/${square}.png`} alt="chess-piece" class="pointer-events-none" />
				{/if}
			</button>
		{/each}
	{/each}
</div>
