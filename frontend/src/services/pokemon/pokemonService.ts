import { pokeApiClient } from '@services/http/client';

export interface PokemonType {
  name: string;
}

export interface PokemonStat {
  name: string;
  value: number;
}

export interface PokemonData {
  id: number;
  name: string;
  height: number;
  weight: number;
  imageUrl: string;
  officialArtwork: string;
  types: PokemonType[];
  abilities: string[];
  moves: Array<{ name: string; learnLevel: number }>;
  evolutionChain: string[];
  stats: PokemonStat[];
}

interface PokemonApiResponse {
  id: number;
  name: string;
  height: number;
  weight: number;
  sprites: {
    other: {
      'official-artwork': {
        front_default: string | null;
      };
    };
  };
  types: Array<{
    type: { name: string };
  }>;
  species: {
    url: string;
  };
  abilities: Array<{
    ability: { name: string };
  }>;
  stats: Array<{
    base_stat: number;
    stat: { name: string };
  }>;
  moves: Array<{
    move: { name: string };
    version_group_details: Array<{
      level_learned_at: number;
      move_learn_method: { name: string };
    }>;
  }>;
}

interface SpeciesResponse {
  evolution_chain: { url: string };
}

interface EvolutionChainResponse {
  chain: {
    species: { name: string };
    evolves_to: EvolutionChainResponse['chain'][];
  };
}

const extractEvolutionNames = (chain: EvolutionChainResponse['chain']): string[] => {
  const names: string[] = [];

  const walk = (node: EvolutionChainResponse['chain']) => {
    names.push(node.species.name);
    node.evolves_to.forEach((next) => walk(next));
  };

  walk(chain);
  return names;
};

const extractMoves = (moves: PokemonApiResponse['moves']) => {
  const registry = new Map<string, number>();

  moves.forEach((entry) => {
    entry.version_group_details.forEach((detail) => {
      if (detail.move_learn_method.name !== 'level-up') {
        return;
      }
      const previous = registry.get(entry.move.name);
      if (previous === undefined || detail.level_learned_at < previous) {
        registry.set(entry.move.name, detail.level_learned_at);
      }
    });
  });

  return Array.from(registry.entries())
    .map(([name, learnLevel]) => ({ name, learnLevel }))
    .sort((a, b) => a.learnLevel - b.learnLevel)
    .slice(0, 20);
};

const buildPokemonImageUrl = (id: number): string =>
  `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png`;

export const searchPokemon = async (query: string): Promise<PokemonData> => {
  const normalizedQuery = query.trim().toLowerCase();
  const response = await pokeApiClient.get<PokemonApiResponse>(
    `/pokemon/${encodeURIComponent(normalizedQuery)}`,
  );

  const data = response.data;
  const speciesResponse = await pokeApiClient.get<SpeciesResponse>(data.species.url);
  const evolutionResponse = await pokeApiClient.get<EvolutionChainResponse>(
    speciesResponse.data.evolution_chain.url,
  );

  return {
    id: data.id,
    name: data.name,
    height: data.height,
    weight: data.weight,
    imageUrl: buildPokemonImageUrl(data.id),
    officialArtwork: data.sprites.other['official-artwork'].front_default ?? '',
    types: data.types.map((entry) => ({ name: entry.type.name })),
    abilities: data.abilities.map((entry) => entry.ability.name),
    moves: extractMoves(data.moves),
    evolutionChain: extractEvolutionNames(evolutionResponse.data.chain),
    stats: data.stats.map((entry) => ({
      name: entry.stat.name,
      value: entry.base_stat,
    })),
  };
};
