import { useEffect, useRef, useState } from 'react';
import { type GameSave, gameService } from '../../../services/game/gameService';
import { type OwnedPokemon, listMyPokemon } from '../../../services/trainer/trainerPokemonService';
import PhaserGame, { type DpadState } from '../PhaserGame';
import './styles.scss';

type GameStatus = 'off' | 'loading' | 'running' | 'error';
type Overlay = 'none' | 'menu' | 'party';

/** Dimensiones internas del canvas de juego */
const GAME_WIDTH  = 320;
const GAME_HEIGHT = 288;

const KEY_DIR: Record<string, 'up' | 'down' | 'left' | 'right'> = {
  ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right',
};

export default function GameShell() {
  // ── Estados ──────────────────────────────────────────────────────────
  const [status, setStatus] = useState<GameStatus>('off');
  const [saveData, setSaveData] = useState<GameSave | null>(null);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [overlay, setOverlay] = useState<Overlay>('none');
  const [dialogText, setDialogText] = useState<string | null>(null);
  const [currentLineIndex, setCurrentLineIndex] = useState(0);
  const [allPokemon, setAllPokemon] = useState<OwnedPokemon[] | null>(null);
  const [keysDown, setKeysDown] = useState({ up: false, down: false, left: false, right: false });

  // ── Refs ─────────────────────────────────────────────────────────────
  const lastKnownPosRef = useRef({ tileX: 5, tileY: 7, mapKey: 'pine_town' });
  const saveDataRef = useRef<GameSave | null>(null);
  const statusRef = useRef<GameStatus>('off');
  const overlayRef = useRef<Overlay>('none');
  const dialogRef = useRef<string | null>(null);
  const gameContainerRef = useRef<HTMLDivElement>(null);
  const isGameFocusedRef = useRef<boolean>(false);
  const dpadRef = useRef<DpadState>({
    up: false, down: false, left: false, right: false, interact: false, blocked: false,
  });

  // ── Función para forzar el foco solo cuando es necesario ────────────
  const forceFocus = (e?: React.SyntheticEvent) => {
    if (e) e.preventDefault();
    if (gameContainerRef.current && document.activeElement !== gameContainerRef.current) {
      // Solo forzar foco si el juego está running y no hay inputs activos
      if (statusRef.current === 'running' && 
          !(document.activeElement instanceof HTMLInputElement || 
            document.activeElement instanceof HTMLTextAreaElement ||
            document.activeElement instanceof HTMLSelectElement)) {
        gameContainerRef.current.focus();
        isGameFocusedRef.current = true;
      }
    }
  };

  // ── Efectos ──────────────────────────────────────────────────────────

  // Prevenir zoom en móviles y selección de texto
  useEffect(() => {
    // Prevenir gestos de zoom con dos dedos
    const preventTouchZoom = (e: TouchEvent) => {
      if (e.touches.length > 1) {
        e.preventDefault();
      }
    };

    // Prevenir zoom con Ctrl + rueda o Cmd + rueda
    const preventWheelZoom = (e: WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
      }
    };

    // Prevenir selección de texto en toda la interfaz del juego
    const preventTextSelection = (e: Event) => {
      const target = e.target as HTMLElement;
      // Permitir selección en inputs y textareas
      if (target instanceof HTMLInputElement || 
          target instanceof HTMLTextAreaElement ||
          target instanceof HTMLSelectElement) {
        return;
      }
      e.preventDefault();
    };

    // Prevenir menú contextual (long press) en móviles
    const preventContextMenu = (e: Event) => {
      const target = e.target as HTMLElement;
      if (target instanceof HTMLInputElement || 
          target instanceof HTMLTextAreaElement ||
          target instanceof HTMLSelectElement) {
        return;
      }
      e.preventDefault();
    };

    // Agregar listeners para prevenir zoom
    document.addEventListener('touchmove', preventTouchZoom, { passive: false });
    document.addEventListener('wheel', preventWheelZoom, { passive: false });
    
    // Agregar listeners para prevenir selección de texto y menú contextual
    document.addEventListener('selectstart', preventTextSelection);
    document.addEventListener('contextmenu', preventContextMenu);

    return () => {
      document.removeEventListener('touchmove', preventTouchZoom);
      document.removeEventListener('wheel', preventWheelZoom);
      document.removeEventListener('selectstart', preventTextSelection);
      document.removeEventListener('contextmenu', preventContextMenu);
    };
  }, []);

  // Solo forzar foco cuando se hace clic en el contenedor del juego
  useEffect(() => {
    const handleContainerClick = () => {
      if (statusRef.current === 'running') {
        gameContainerRef.current?.focus();
        isGameFocusedRef.current = true;
      }
    };

    const container = gameContainerRef.current;
    if (container) {
      container.addEventListener('click', handleContainerClick);
      return () => container.removeEventListener('click', handleContainerClick);
    }
  }, []);

  // Manejar pérdida de foco solo si es causada por elementos no interactivos
  useEffect(() => {
    const handleFocusOut = (e: FocusEvent) => {
      // Si el juego está running y el foco se pierde hacia un elemento no interactivo
      if (statusRef.current === 'running' && 
          gameContainerRef.current && 
          e.relatedTarget instanceof HTMLElement) {
        const target = e.relatedTarget;
        // No robar foco si es un input, textarea, select o elemento editable
        if (!(target instanceof HTMLInputElement || 
              target instanceof HTMLTextAreaElement ||
              target instanceof HTMLSelectElement ||
              target.isContentEditable)) {
          // Pero tampoco robarlo agresivamente, solo si es necesario
          setTimeout(() => {
            if (document.activeElement !== gameContainerRef.current) {
              gameContainerRef.current?.focus();
              isGameFocusedRef.current = true;
            }
          }, 50);
        }
      }
    };

    document.addEventListener('focusout', handleFocusOut);
    return () => document.removeEventListener('focusout', handleFocusOut);
  }, []);

  // Manejar eventos de foco para trackear el estado
  useEffect(() => {
    const handleFocus = () => {
      isGameFocusedRef.current = true;
    };
    const handleBlur = () => {
      isGameFocusedRef.current = false;
    };

    const container = gameContainerRef.current;
    if (container) {
      container.addEventListener('focus', handleFocus);
      container.addEventListener('blur', handleBlur);
      return () => {
        container.removeEventListener('focus', handleFocus);
        container.removeEventListener('blur', handleBlur);
      };
    }
  }, []);

  useEffect(() => { saveDataRef.current = saveData; }, [saveData]);
  useEffect(() => { statusRef.current = status; }, [status]);
  useEffect(() => { overlayRef.current = overlay; }, [overlay]);
  useEffect(() => {
    dialogRef.current = dialogText;
    if (dialogText !== null) {
      setCurrentLineIndex(0);
    }
  }, [dialogText]);
  
  useEffect(() => {
    dpadRef.current.blocked = overlay !== 'none' || dialogText !== null;
  }, [overlay, dialogText]);

  // Load existing save on mount
  useEffect(() => {
    gameService.loadSave()
      .then((s) => {
        setSaveData(s);
        saveDataRef.current = s;
        lastKnownPosRef.current = {
          tileX: s.tile_x ?? 5,
          tileY: s.tile_y ?? 7,
          mapKey: s.map_id ?? 'pine_town'
        };
      })
      .catch(() => setSaveData(null));
  }, []);

  // ── FILTRO: La barra espaciadora NO afecta al diálogo ──────────────
  useEffect(() => {
    const filterSpace = (e: KeyboardEvent) => {
      if (e.code === 'Space' && dialogText !== null) {
        e.stopPropagation();
      }
    };

    document.addEventListener('keydown', filterSpace, true);
    return () => {
      document.removeEventListener('keydown', filterSpace, true);
    };
  }, [dialogText]);

  // ── ENFOQUE DEFINITIVO ──────────────────────────────────────────────
  useEffect(() => {
    if (status === 'running') {
      setTimeout(() => {
        if (gameContainerRef.current && document.activeElement !== gameContainerRef.current) {
          gameContainerRef.current.focus();
          isGameFocusedRef.current = true;
        }
      }, 100);
    }
  }, [status]);

  // ── Acción unificada de interacción ─────────────────────────────────
  const handleInteractAction = () => {
    if (dialogRef.current !== null) {
      const lines = dialogRef.current.split('\n').filter(line => line.trim() !== '');
      setCurrentLineIndex(prev => {
        if (prev < lines.length - 1) return prev + 1;
        setDialogText(null);
        dialogRef.current = null;
        dpadRef.current.interact = false;
        return 0;
      });
      return;
    }

    if (overlayRef.current !== 'none') return;
    if (statusRef.current !== 'running') return;
    dpadRef.current.interact = true;
    setTimeout(() => { dpadRef.current.interact = false; }, 80);
  };

  // ── Teclado ──────────────────────────────────────────────────────────
  useEffect(() => {
    const onDown = (e: KeyboardEvent) => {
      // Si el foco está en un campo de texto u otro elemento interactivo
      // o si el juego no tiene foco, dejar pasar el evento
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (e.target as HTMLElement)?.isContentEditable) {
        return;
      }

      // Enter → START (arrancar / pausar-reanudar) 
      // Esto funciona incluso cuando el juego está apagado
      if (e.code === 'Enter') {
        e.preventDefault();
        e.stopPropagation();
        handleStart();
        return;
      }

      // Solo procesar el resto de teclas del juego si el juego está running y tiene foco
      if (statusRef.current !== 'running' || !isGameFocusedRef.current) {
        return;
      }

      const dir = KEY_DIR[e.code];
      if (dir) {
        e.preventDefault();
        e.stopPropagation();
        dpadRef.current[dir] = true;
        setKeysDown((p) => p[dir] ? p : { ...p, [dir]: true });
        return;
      }

      // Space → SELECT (party / avanzar diálogo)
      if (e.code === 'Space') {
        e.preventDefault();
        e.stopPropagation();
        handleSelect();
        return;
      }

      // Z → interacción con el mundo (signos, NPCs)
      if (e.code === 'KeyZ') {
        e.preventDefault();
        e.stopPropagation();
        handleInteractAction();
        return;
      }

      if (e.code === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        setOverlay('none');
      }
    };

    const onUp = (e: KeyboardEvent) => {
      // Solo procesar si el juego tiene foco
      if (statusRef.current !== 'running' || !isGameFocusedRef.current) {
        return;
      }

      const dir = KEY_DIR[e.code];
      if (dir) {
        dpadRef.current[dir] = false;
        setKeysDown((p) => p[dir] ? { ...p, [dir]: false } : p);
        return;
      }
      if (e.code === 'KeyZ') {
        dpadRef.current.interact = false;
      }
    };

    // Usar capture phase para asegurar que el shell maneje las teclas antes
    // que otros listeners en la página
    window.addEventListener('keydown', onDown, true);
    window.addEventListener('keyup', onUp, true);
    
    return () => {
      window.removeEventListener('keydown', onDown, true);
      window.removeEventListener('keyup', onUp, true);
    };
  }, []);

  // ── Actions ──────────────────────────────────────────────────────────
  const handleStart = async () => {
    if (statusRef.current === 'loading') return;
    
    // Si el juego está running, alternar el menú de pausa
    if (statusRef.current === 'running') {
      setOverlay((o) => o === 'menu' ? 'none' : 'menu');
      return;
    }
    
    // Si el juego está apagado, iniciarlo
    if (statusRef.current === 'off') {
      setStatus('loading');
      try {
        let save = saveDataRef.current;
        if (!save) save = await gameService.newGame();
        setSaveData(save);
        saveDataRef.current = save;
        lastKnownPosRef.current = {
          tileX: save.tile_x ?? 5,
          tileY: save.tile_y ?? 7,
          mapKey: save.map_id ?? 'pine_town'
        };
        setStatus('running');
        // Dar foco al juego después de iniciar
        setTimeout(() => {
          gameContainerRef.current?.focus();
          isGameFocusedRef.current = true;
        }, 50);
      } catch {
        setStatus('error');
      }
    }
  };

  const openParty = async () => {
    if (!allPokemon) {
      try {
        setAllPokemon(await listMyPokemon());
      } catch {
        return;
      }
    }
    setOverlay('party');
  };

  const handleSelect = async () => {
    if (statusRef.current !== 'running') return;
    if (overlayRef.current === 'party') {
      setOverlay('none');
      return;
    }
    await openParty();
  };

  const handleManualSave = async () => {
    const sd = saveDataRef.current;
    if (!sd || saveStatus === 'saving') return;
    setSaveStatus('saving');
    try {
      const { tileX, tileY, mapKey } = lastKnownPosRef.current;
      const updated = await gameService.saveGame({ map_id: mapKey, tile_x: tileX, tile_y: tileY });
      saveDataRef.current = updated;
      setSaveData(updated);
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
    setOverlay('none');
  };

  const handleShutdown = async () => {
    if (saveDataRef.current) {
      const { tileX, tileY, mapKey } = lastKnownPosRef.current;
      try {
        await gameService.saveGame({ map_id: mapKey, tile_x: tileX, tile_y: tileY });
      } catch {
        /* ok */
      }
    }
    setStatus('off');
    setOverlay('none');
    setDialogText(null);
    dialogRef.current = null;
    setSaveStatus('idle');
    isGameFocusedRef.current = false;
  };

  const handleAutosave = async (tileX: number, tileY: number, mapKey: string) => {
    lastKnownPosRef.current = { tileX, tileY, mapKey };
    try {
      const updated = await gameService.saveGame({ map_id: mapKey, tile_x: tileX, tile_y: tileY });
      saveDataRef.current = updated;
      setSaveData(updated);
    } catch {
      /* silent */
    }
  };

  // ── Input helpers ────────────────────────────────────────────────────
  const pressDpad = (dir: 'up' | 'down' | 'left' | 'right') => {
    if (statusRef.current !== 'running') return;
    dpadRef.current[dir] = true;
    setKeysDown((p) => ({ ...p, [dir]: true }));
  };

  const releaseDpad = (dir: 'up' | 'down' | 'left' | 'right') => {
    if (statusRef.current !== 'running') return;
    dpadRef.current[dir] = false;
    setKeysDown((p) => ({ ...p, [dir]: false }));
  };

  const handleAPress = () => {
    if (statusRef.current !== 'running') return;
    handleInteractAction();
  };

  const handleARelease = () => {
    dpadRef.current.interact = false;
  };

  const handleBPress = () => {
    if (statusRef.current !== 'running') return;
    if (dialogText !== null) {
      setDialogText(null);
      setCurrentLineIndex(0);
      dialogRef.current = null;
      return;
    }
    if (overlay !== 'none') setOverlay('none');
  };

  // ── Party data ──────────────────────────────────────────────────────
  const partySlots = Array.from({ length: 6 }).map((_, i) => {
    const slot = saveData?.party_slots?.find((s) => s.slot_position === i);
    if (!slot) return null;
    return allPokemon?.find((p) => p.id === slot.trainer_pokemon_id) ?? null;
  });

  // ── Constantes de UI ──────────────────────────────────────────────────
  const startLabel = 'START'

  // ── Render ──────────────────────────────────────────────────────────
  return (
    <div 
      className="gbc"
      style={{
        userSelect: 'none',
        WebkitUserSelect: 'none',
        WebkitTouchCallout: 'none',
        touchAction: 'none',
      }}
    >
      {/* Header */}
      <div className="gbc__header">
        <div className="gbc__power-indicator">
          <span className={`gbc__power-led${status === 'running' ? ' gbc__power-led--on' : ''}`} />
          <span className="gbc__power-label">PWR</span>
        </div>
        <span className="gbc__brand">PokeTrainer</span>
        <span className={`gbc__save-toast${saveStatus !== 'idle' ? ` gbc__save-toast--${saveStatus}` : ' gbc__save-toast--hidden'}`}>
          {saveStatus === 'saving' ? 'Guardando…' : saveStatus === 'saved' ? '✓ Guardado' : '✗ Error'}
        </span>
      </div>

      {/* Screen bezel */}
      <div className="gbc__bezel">
        {status === 'off' && (
          <div className="gbc__screen-off">
            <span className="gbc__screen-title">PokeTrainer</span>
            {saveData && (
              <span className="gbc__screen-subtitle">
                {saveData.map_id.replace(/_/g, ' ')} · {Math.floor((saveData.play_time_seconds ?? 0) / 60)}m
              </span>
            )}
          </div>
        )}

        {status === 'loading' && (
          <div className="gbc__screen-off">
            <div className="gbc__loading-bar-wrap">
              <div className="gbc__loading-bar" />
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="gbc__screen-off">
            <span className="gbc__screen-title gbc__screen-title--error">ERROR</span>
            <button className="gbc__menu-btn" onClick={() => setStatus('off')}>Volver</button>
          </div>
        )}

        {status === 'running' && (
          <div
            ref={gameContainerRef}
            className="gbc__game-wrapper"
            tabIndex={0}
            style={{ 
              outline: 'none',
              width: GAME_WIDTH,
              height: GAME_HEIGHT,
              flexShrink: 0,
              userSelect: 'none',
              WebkitUserSelect: 'none',
              touchAction: 'none',
            }}
          >
            <PhaserGame
              width={GAME_WIDTH}
              height={GAME_HEIGHT}
              initMapKey={saveData?.map_id ?? 'pine_town'}
              initTileX={saveData?.tile_x ?? 5}
              initTileY={saveData?.tile_y ?? 7}
              dpadState={dpadRef.current}
              onSave={handleAutosave}
              onInteract={(msg) => setDialogText(msg)}
            />
          </div>
        )}

        {/* Dialog overlay */}
        {dialogText && (() => {
          const lines = dialogText.split('\n').filter(line => line.trim() !== '');
          const currentLine = lines[currentLineIndex] || '';
          return (
            <div 
              className="gbc__dialog"
              style={{
                userSelect: 'none',
                WebkitUserSelect: 'none',
              }}
            >
              <div className="gbc__dialog-text">{currentLine}</div>
              <span className="gbc__dialog-hint">▼</span>
            </div>
          );
        })()}

        {/* Party overlay */}
        {overlay === 'party' && (
          <div 
            className="gbc__overlay"
            style={{
              userSelect: 'none',
              WebkitUserSelect: 'none',
            }}
          >
            <div className="gbc__overlay-header">
              <span>POKÉMON</span>
              <button className="gbc__overlay-close" onClick={() => setOverlay('none')}>✕</button>
            </div>
            <div className="gbc__party-slots">
              {partySlots.map((mon, i) => (
                <div key={i} className={`gbc__party-slot${!mon ? ' gbc__party-slot--empty' : ''}`}>
                  {mon ? (
                    <>
                      <img
                        className="gbc__party-sprite"
                        src={`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${mon.pokemon.pokeapi_id}.png`}
                        alt={mon.pokemon.name}
                        draggable={false}
                      />
                      <div className="gbc__party-info">
                        <span className="gbc__party-name">{mon.pokemon.name.toUpperCase()}</span>
                        <span className="gbc__party-level">Lv.{mon.current_level}</span>
                        <div className="gbc__hp-bar">
                          <div
                            className="gbc__hp-fill"
                            style={{
                              width: `${Math.round((mon.current_hp / mon.max_hp) * 100)}%`,
                              backgroundColor:
                                mon.current_hp / mon.max_hp > 0.5 ? '#56d364'
                                : mon.current_hp / mon.max_hp > 0.2 ? '#e3b341' : '#f85149',
                            }}
                          />
                        </div>
                        <span className="gbc__hp-text">{mon.current_hp}/{mon.max_hp} HP</span>
                      </div>
                    </>
                  ) : (
                    <span className="gbc__party-empty">─</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pause menu overlay */}
        {overlay === 'menu' && (
          <div 
            className="gbc__overlay gbc__overlay--menu"
            style={{
              userSelect: 'none',
              WebkitUserSelect: 'none',
            }}
          >
            <p className="gbc__menu-title">PAUSA</p>
            <button className="gbc__menu-btn" onClick={handleManualSave} disabled={saveStatus === 'saving'}>
              {saveStatus === 'saving' ? 'GUARDANDO…' : 'GUARDAR'}
            </button>
            <button className="gbc__menu-btn" onClick={async () => { setOverlay('none'); await openParty(); }}>
              POKÉMON
            </button>
            <button className="gbc__menu-btn" onClick={() => setOverlay('none')}>CONTINUAR</button>
            <button className="gbc__menu-btn gbc__menu-btn--danger" onClick={handleShutdown}>APAGAR</button>
          </div>
        )}
      </div>

      {/* Controls */}
      <div 
        className="gbc__controls" 
        onContextMenu={(e) => e.preventDefault()}
        style={{
          userSelect: 'none',
          WebkitUserSelect: 'none',
          touchAction: 'none',
        }}
      >
        {/* D-pad */}
        <div className="gbc__dpad">
          <div className="gbc__dpad-cross" />
          <button
            className={`dpad-btn dpad-btn--up${keysDown.up ? ' dpad-btn--active' : ''}`}
            onPointerDown={(e) => { e.preventDefault(); forceFocus(e); pressDpad('up'); }}
            onPointerUp={() => releaseDpad('up')}
            onPointerLeave={() => releaseDpad('up')}
            aria-label="Up"
            style={{ touchAction: 'none' }}
          >▲</button>
          <button
            className={`dpad-btn dpad-btn--left${keysDown.left ? ' dpad-btn--active' : ''}`}
            onPointerDown={(e) => { e.preventDefault(); forceFocus(e); pressDpad('left'); }}
            onPointerUp={() => releaseDpad('left')}
            onPointerLeave={() => releaseDpad('left')}
            aria-label="Left"
            style={{ touchAction: 'none' }}
          >◀</button>
          <div className="dpad-btn dpad-btn--mid" />
          <button
            className={`dpad-btn dpad-btn--right${keysDown.right ? ' dpad-btn--active' : ''}`}
            onPointerDown={(e) => { e.preventDefault(); forceFocus(e); pressDpad('right'); }}
            onPointerUp={() => releaseDpad('right')}
            onPointerLeave={() => releaseDpad('right')}
            aria-label="Right"
            style={{ touchAction: 'none' }}
          >▶</button>
          <button
            className={`dpad-btn dpad-btn--down${keysDown.down ? ' dpad-btn--active' : ''}`}
            onPointerDown={(e) => { e.preventDefault(); forceFocus(e); pressDpad('down'); }}
            onPointerUp={() => releaseDpad('down')}
            onPointerLeave={() => releaseDpad('down')}
            aria-label="Down"
            style={{ touchAction: 'none' }}
          >▼</button>
        </div>

        {/* SELECT + START */}
        <div className="gbc__mid-buttons">
          <button
            type="button"
            className="gbc__sys-btn"
            onMouseDown={(e) => e.preventDefault()}
            onClick={(e) => { forceFocus(e); handleSelect(); }}
            disabled={status !== 'running'}
            style={{ touchAction: 'none' }}
          >SELECT</button>
          <button
            type="button"
            className="gbc__sys-btn gbc__sys-btn--start"
            onMouseDown={(e) => e.preventDefault()}
            onClick={(e) => { forceFocus(e); handleStart(); }}
            disabled={status === 'loading'}
            style={{ touchAction: 'none' }}
          >
            {startLabel}
          </button>
        </div>

        {/* Speaker dots */}
        <div className="gbc__speaker">
          {Array.from({ length: 4 }).map((_, r) => (
            <div key={r} className="gbc__speaker-row">
              {Array.from({ length: 4 }).map((_, c) => (
                <span key={c} className="gbc__speaker-dot" />
              ))}
            </div>
          ))}
        </div>

        {/* A / B buttons */}
        <div className="gbc__ab-group">
          <button
            type="button"
            className="gbc__ab-btn gbc__b-btn"
            onMouseDown={(e) => e.preventDefault()}
            onPointerDown={(e) => { forceFocus(e); handleBPress(); }}
            aria-label="B"
            style={{ touchAction: 'none' }}
          >B</button>
          <button
            type="button"
            className="gbc__ab-btn gbc__a-btn"
            onMouseDown={(e) => e.preventDefault()}
            onPointerDown={(e) => { forceFocus(e); handleAPress(); }}
            onPointerUp={() => handleARelease()}
            onPointerLeave={() => handleARelease()}
            aria-label="A"
            style={{ touchAction: 'none' }}
          >A</button>
        </div>
      </div>

      {/* Footer */}
      <div className="gbc__footer">
        <span className="gbc__footer-text">GameBox Color™</span>
      </div>
    </div>
  );
}