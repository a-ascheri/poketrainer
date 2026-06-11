// components/Pokemon/PokemonSearchModal/index.tsx
import { useEffect, useState } from 'react';
import PokemonCard from '../PokemonCard';
import PokemonDetails from '../PokemonDetails';
import { type PokemonData } from '../../../services/pokemon/pokemonService';
import './styles.scss';

interface PokemonSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function PokemonSearchModal({ isOpen, onClose }: PokemonSearchModalProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [pokemonData, setPokemonData] = useState<PokemonData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  // Cerrar con ESC
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleClose = () => {
    setSearchTerm('');
    setPokemonData(null);
    setError(null);
    setShowDetails(false);
    onClose();
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setLoading(true);
    setError(null);
    setPokemonData(null);
    setShowDetails(false);

    try {
      const response = await fetch(`/api/v1/pokemon/${searchTerm.toLowerCase()}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Pokémon "${searchTerm}" no encontrado`);
        }
        if (response.status === 422) {
          throw new Error('Nombre de Pokémon inválido (usa solo letras, números, guiones o apóstrofes)');
        }
        throw new Error('Error al buscar el Pokémon');
      }
      
      const data = await response.json();
      setPokemonData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={handleClose} />
      <div className="pokemon-search-modal">
        <button className="pokemon-search-modal__close" onClick={handleClose}>
          ✕
        </button>

        <div className="pokemon-search-modal__header">
          <h2 className="pokemon-search-modal__title">🔍 Pokédex</h2>
          <p className="pokemon-search-modal__subtitle">Buscá por nombre o ID</p>
        </div>

        <form onSubmit={handleSearch} className="pokemon-search-modal__form">
          <input
            type="text"
            placeholder="Ej: Pikachu, 25, Charizard..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            autoFocus
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </form>

        {error && (
          <div className="pokemon-search-modal__error">
            ❌ {error}
          </div>
        )}

        {pokemonData && !showDetails && (
          <div 
            className="pokemon-search-modal__card"
            onClick={() => setShowDetails(true)}
            style={{ cursor: 'pointer' }}
          >
            <PokemonCard pokemon={pokemonData} />
            <div className="pokemon-search-modal__expand-hint">
              Clickeá para ver más detalles
            </div>
          </div>
        )}

        {pokemonData && showDetails && (
          <div className="pokemon-search-modal__details">
            <button 
              className="pokemon-search-modal__back"
              onClick={() => setShowDetails(false)}
            >
              ← Volver a la tarjeta
            </button>
            <PokemonDetails pokemon={pokemonData} />
          </div>
        )}
      </div>
    </>
  );
}