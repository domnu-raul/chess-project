<script lang="ts">
	import { onMount } from 'svelte';
	import { Game, Piece } from './chessGame.ts';

	const game = new Game();
	let change = false;

	onMount(async () => {
		const response = await fetch('http://localhost:8000/start', { method: 'POST' });
		const obj = await response.json();

		await game.setKey(obj.key);
	});
</script>

{#key change}
	<div class="grid grid-rows-8 grid-cols-8 w-[600px] h-[600px]">
		{#each { length: 8 } as _, y}
			{#each { length: 8 } as _, x}
				{@const position = game.translatePosition({ x, y })}
				{@const square = game.getSquare(position)}
				{@const piece = square.getPiece()}
				{@const hl = square.isHighlighted()}

				<button
					on:click={async () => {
						await game.tryMove(position);
						change = !change;
					}}
					class={`${(x + y) % 2 == 0 ? 'bg-slate-300' : 'bg-green-700'} flex flex-row-reverse ${hl && piece !== Piece.NONE ? 'ring-4 ring-inset ring-yellow-300' : ''}`}
					id={`${position}`}
				>
					{#if x == 0}
						<span
							class={`z-[1] m-[1px] text-sm font-medium ${(x + y) % 2 == 0 ? 'text-slate-700' : 'text-slate-200'} absolute start-0`}
							>{Math.abs(y - 8)}</span
						>
					{/if}

					{#if y == 7}
						<span
							class={`z-[1] m-[1px] text-sm font-medium ${(x + y) % 2 == 0 ? 'text-slate-700' : 'text-slate-200'} absolute self-end`}
							>{`${String.fromCharCode(65 + x)}`}</span
						>
					{/if}

					{#if piece !== Piece.NONE}
						<img src={`pieces/${piece}.png`} alt="chess-piece" class="pointer-events-none" />
					{:else if hl}
						<span class="rounded-full w-6 h-6 self-center m-auto bg-slate-600"></span>
					{/if}
				</button>
			{/each}
		{/each}
	</div>
{/key}
