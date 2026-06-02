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
  const [status,     setStatus]     = useState<GameStatus>('off');
  const [saveData,   setSaveData]   = useState<GameSave | null>(null);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [overlay,    setOverlay]    = useState<Overlay>('none');
  const [dialogText, setDialogText] = useState<string | null>(null);
  const [allPokemon, setAllPokemon] = useState<OwnedPokemon[] | null>(null);
  const [keysDown,   setKeysDown]   = useState({ up: false, down: false, left: false, right: false });

  const lastKnownPosRef = useRef({ tileX: 5, tileY: 7, mapKey: 'pallet_town' });
  const saveDataRef     = useRef<GameSave | null>(null);
  const statusRef       = useRef<GameStatus>('off');
  const overlayRef      = useRef<Overlay>('none');
  const dialogRef       = useRef<string | null>(null);
  const dpadRef         = useRef<DpadState>({
    up: false, down: false, left: false, right: false, interact: false, blocked: false,
  });

  useEffect(() => { saveDataRef.current = saveData;   }, [saveData]);
  useEffect(() => { statusRef.current   = status;     }, [status]);
  useEffect(() => { overlayRef.current  = overlay;    }, [overlay]);
  useEffect(() => { dialogRef.current   = dialogText; }, [dialogText]);
  useEffect(() => { dpadRef.current.blocked = overlay !== 'none' || dialogText !== null; }, [overlay, dialogText]);

  // Load existing save on mount
  useEffect(() => {
    gameService.loadSave().then((s) => {
      setSaveData(s);
      saveDataRef.current = s;
      lastKnownPosRef.current = { tileX: s.tile_x ?? 5, tileY: s.tile_y ?? 7, mapKey: s.map_id ?? 'pallet_town' };
    }).catch(() => setSaveData(null));
  }, []);

  // Global keyboard listener — uses refs, registered once
  useEffect(() => {
    const handleInteract = () => {
      if (dialogRef.current !== null) {
        dialogRef.current = null;
        setDialogText(null);
        dpadRef.current.interact = false;
        return;
      }
      if (overlayRef.current !== 'none') return;
      if (statusRef.current !== 'running') return;
      dpadRef.current.interact = true;
      setTimeout(() => { dpadRef.current.interact = false; }, 80);
    };

    const onDown = (e: KeyboardEvent) => {
      const dir = KEY_DIR[e.code];
      if (dir) { dpadRef.current[dir] = true; setKeysDown((p) => p[dir] ? p : { ...p, [dir]: true }); return; }
      if (e.code === 'Space' || e.code === 'KeyZ') { e.preventDefault(); handleInteract(); }
      if (e.code === 'Escape') setOverlay('none');
    };
    const onUp = (e: KeyboardEvent) => {
      const dir = KEY_DIR[e.code];
      if (dir) { dpadRef.current[dir] = false; setKeysDown((p) => p[dir] ? { ...p, [dir]: false } : p); }
      if (e.code === 'Space' || e.code === 'KeyZ') dpadRef.current.interact = false;
    };

    window.addEventListener('keydown', onDown);
    window.addEventListener('keyup', onUp);
    return () => { window.removeEventListener('keydown', onDown); window.removeEventListener('keyup', onUp); };
  }, []);

  // ── Actions ────────────────────────────────────────────────────────────

  const handleStart = async () => {
    if (status === 'loading') return;
    if (status === 'running') { setOverlay((o) => o === 'menu' ? 'none' : 'menu'); return; }
    setStatus('loading');
    try {
      let save = saveDataRef.current;
      if (!save) save = await gameService.newGame();
      setSaveData(save);
      saveDataRef.current = save;
      lastKnownPosRef.current = { tileX: save.tile_x ?? 5, tileY: save.tile_y ?? 7, mapKey: save.map_id ?? 'pallet_town' };
      setStatus('running');
    } catch { setStatus('error'); }
  };

  const openParty = async () => {
    if (!allPokemon) {
      try { setAllPokemon(await listMyPokemon()); } catch { return; }
    }
    setOverlay('party');
  };

  const handleSelect = async () => {
    if (status !== 'running') return;
    if (overlay === 'party') { setOverlay('none'); return; }
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
      try { await gameService.saveGame({ map_id: mapKey, tile_x: tileX, tile_y: tileY }); } catch { /* ok */ }
    }
    setStatus('off');
    setOverlay('none');
    setDialogText(null);
    dialogRef.current = null;
    setSaveStatus('idle');
  };

  const handleAutosave = async (tileX: number, tileY: number, mapKey: string) => {
    lastKnownPosRef.current = { tileX, tileY, mapKey };
    try {
      const updated = await gameService.saveGame({ map_id: mapKey, tile_x: tileX, tile_y: tileY });
      saveDataRef.current = updated;
      setSaveData(updated);
    } catch { /* silent */ }
  };

  // ── Input helpers ──────────────────────────────────────────────────────

  const pressDpad  = (dir: 'up' | 'down' | 'left' | 'right') => { dpadRef.current[dir] = true;  setKeysDown((p) => ({ ...p, [dir]: true  })); };
  const releaseDpad = (dir: 'up' | 'down' | 'left' | 'right') => { dpadRef.current[dir] = false; setKeysDown((p) => ({ ...p, [dir]: false })); };

  const handleAPress = () => {
    if (dialogText !== null) { setDialogText(null); dialogRef.current = null; dpadRef.current.interact = false; return; }
    if (overlay !== 'none') return;
    if (status !== 'running') return;
    dpadRef.current.interact = true;
  };
  const handleARelease = () => { dpadRef.current.interact = false; };

  const handleBPress = () => {
    if (dialogText !== null) { setDialogText(null); dialogRef.current = null; return; }
    if (overlay !== 'none') setOverlay('none');
  };

  // ── Party data ─────────────────────────────────────────────────────────

  const partySlots = Array.from({ length: 6 }).map((_, i) => {
    const slot = saveData?.party_slots?.find((s) => s.slot_position === i);
    if (!slot) return null;
    return allPokemon?.find((p) => p.id === slot.trainer_pokemon_id) ?? null;
  });

  const startLabel = status === 'off' ? (saveData ? 'CONTINUE' : 'START') : 'START';

  return (
    <div className="gbc">
      {/* ── Header ─────────────────────────────────────────────────── */}
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

      {/* ── Screen bezel ────────────────────────────────────────────── */}
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
            <div className="gbc__loading-bar-wrap"><div className="gbc__loading-bar" /></div>
          </div>
        )}

        {status === 'error' && (
          <div className="gbc__screen-off">
            <span className="gbc__screen-title gbc__screen-title--error">ERROR</span>
            <button className="gbc__menu-btn" onClick={() => setStatus('off')}>Volver</button>
          </div>
        )}

        {status === 'running' && (
          <PhaserGame
            width={GAME_WIDTH}
            height={GAME_HEIGHT}
            initMapKey={saveData?.map_id ?? 'pallet_town'}
            initTileX={saveData?.tile_x ?? 5}
            initTileY={saveData?.tile_y ?? 7}
            dpadState={dpadRef.current}
            onSave={handleAutosave}
            onInteract={(msg) => setDialogText(msg)}
          />
        )}

        {/* Dialog overlay */}
        {dialogText && (
          <div className="gbc__dialog">
            <p className="gbc__dialog-text">{dialogText}</p>
            <span className="gbc__dialog-hint">▼</span>
          </div>
        )}

        {/* Party overlay */}
        {overlay === 'party' && (
          <div className="gbc__overlay">
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
          <div className="gbc__overlay gbc__overlay--menu">
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

      {/* ── Controls ────────────────────────────────────────────────── */}
      <div className="gbc__controls" onContextMenu={(e) => e.preventDefault()}>

        {/* D-pad */}
        <div className="gbc__dpad">
          <div className="gbc__dpad-cross" />
          <button
            className={`dpad-btn dpad-btn--up${keysDown.up ? ' dpad-btn--active' : ''}`}
            onPointerDown={() => pressDpad('up')} onPointerUp={() => releaseDpad('up')} onPointerLeave={() => releaseDpad('up')}
            aria-label="Up"
          >▲</button>
          <button
            className={`dpad-btn dpad-btn--left${keysDown.left ? ' dpad-btn--active' : ''}`}
            onPointerDown={() => pressDpad('left')} onPointerUp={() => releaseDpad('left')} onPointerLeave={() => releaseDpad('left')}
            aria-label="Left"
          >◀</button>
          <div className="dpad-btn dpad-btn--mid" />
          <button
            className={`dpad-btn dpad-btn--right${keysDown.right ? ' dpad-btn--active' : ''}`}
            onPointerDown={() => pressDpad('right')} onPointerUp={() => releaseDpad('right')} onPointerLeave={() => releaseDpad('right')}
            aria-label="Right"
          >▶</button>
          <button
            className={`dpad-btn dpad-btn--down${keysDown.down ? ' dpad-btn--active' : ''}`}
            onPointerDown={() => pressDpad('down')} onPointerUp={() => releaseDpad('down')} onPointerLeave={() => releaseDpad('down')}
            aria-label="Down"
          >▼</button>
        </div>

        {/* SELECT + START */}
        <div className="gbc__mid-buttons">
          <button className="gbc__sys-btn" onClick={handleSelect} disabled={status !== 'running'}>SELECT</button>
          <button className="gbc__sys-btn gbc__sys-btn--start" onClick={handleStart} disabled={status === 'loading'}>
            {startLabel}
          </button>
        </div>

        {/* Speaker dots (decorative) */}
        <div className="gbc__speaker">
          {Array.from({ length: 4 }).map((_, r) => (
            <div key={r} className="gbc__speaker-row">
              {Array.from({ length: 4 }).map((_, c) => <span key={c} className="gbc__speaker-dot" />)}
            </div>
          ))}
        </div>

        {/* A / B buttons */}
        <div className="gbc__ab-group">
          <button className="gbc__ab-btn gbc__b-btn" onPointerDown={handleBPress} aria-label="B">B</button>
          <button
            className="gbc__ab-btn gbc__a-btn"
            onPointerDown={handleAPress}
            onPointerUp={handleARelease}
            onPointerLeave={handleARelease}
            aria-label="A"
          >A</button>
        </div>
      </div>

      {/* ── Footer ──────────────────────────────────────────────────── */}
      <div className="gbc__footer">
        <span className="gbc__footer-text">Game Boy Color ™</span>
      </div>
    </div>
  );
}
