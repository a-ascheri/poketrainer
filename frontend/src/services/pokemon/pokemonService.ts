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
  stats: Array<{
    base_stat: number;
    stat: { name: string };
  }>;
}

const buildPokemonImageUrl = (id: number): string =>
  `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png`;

export const searchPokemon = async (query: string): Promise<PokemonData> => {
  const normalizedQuery = query.trim().toLowerCase();
  const response = await pokeApiClient.get<PokemonApiResponse>(
    `/pokemon/${encodeURIComponent(normalizedQuery)}`,
  );

  const data = response.data;

  return {
    id: data.id,
    name: data.name,
    height: data.height,
    weight: data.weight,
    imageUrl: buildPokemonImageUrl(data.id),
    officialArtwork: data.sprites.other['official-artwork'].front_default ?? '',
    types: data.types.map((entry) => ({ name: entry.type.name })),
    stats: data.stats.map((entry) => ({
      name: entry.stat.name,
      value: entry.base_stat,
    })),
  };
};
