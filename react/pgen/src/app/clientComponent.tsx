'use client'

import { useFormState, useFormStatus } from "react-dom";
import { createPlaylistAction, loginAction, searchAction } from "./serverComponents";
import { useEffect, useState } from "react";

const SubmitButton = ({id, defaultText, pendingText, disabled=false, className=''}: {id: string, defaultText: string, pendingText: string, disabled?: boolean, className?: string}) => {
	const { pending } = useFormStatus();

	return (
		<button className={`flex items-center justify-center ${className}`} hidden={defaultText === ''} id={id} type='submit' aria-disabled={pending || disabled} disabled={pending || disabled}>
      {pending && (
        <>
          <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-white"></div>
          <span className="ml-2">{pendingText}</span>
        </>
      )}
      {!pending && defaultText}
    </button>
	)
}

export default function ClientComponent({loggedIn}: {loggedIn: boolean}) {
  const [loginState, formLoginAction] = useFormState(loginAction, {});
  const [searchState, formSearchAction] = useFormState(searchAction, {error: '', object: [], status: 0});
  const [createState, formCreatePlaylistAction] = useFormState(createPlaylistAction, {error: '', object: [], status: 0});
  const [artistsFound, setArtistsFound] = useState(false)
  const [inputValue, setInputValue] = useState('');
  const [selectedArtists, setSelectedArtists] = useState<any[]>([]); // Lista de artistas elegidos
  const [draggedArtist, setDraggedArtist] = useState<any | null>(null); // Artista que se está arrastrando
  const [mouseOffset, setMouseOffset] = useState<{ x: number; y: number }>({x: 0, y: 0});
  const [draggedArtistData, setDraggedArtistData] = useState<any | null>(null);
  const [isDraggingOver, setIsDraggingOver] = useState<boolean[]>([false]);
  const [isDragging, setIsDragging] = useState(false);
  const [isInputFocused, setInputFocused] = useState(false);

  const handleInputFocus = () => {
    setInputFocused(true);
  };

  const handleInputBlur = () => {
    setInputFocused(false);
  };

  const handleMouseDown = (value: any, event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    const originalElement = event.currentTarget;
    const cloneElement = originalElement.cloneNode(true) as HTMLDivElement; // Clonar el elemento
    const rect = originalElement.getBoundingClientRect(); // Obtener las coordenadas del elemento original
    const offsetX = event.clientX - rect.left; // Calcular el desplazamiento X
    const offsetY = event.clientY - rect.top; // Calcular el desplazamiento Y

    // Establecer estilos para la copia
    cloneElement.style.position = 'absolute';
    cloneElement.style.left = `${event.clientX - offsetX}px`;
    cloneElement.style.top = `${event.clientY - offsetY}px`;
    cloneElement.style.width = `${rect.width}px`; // Mantener la misma anchura que el elemento original
    cloneElement.style.height = `${rect.height}px`; // Mantener la misma altura que el elemento original
    cloneElement.style.transform = 'rotate(2deg)'; // Aplicar una ligera rotación al elemento clonado
    cloneElement.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)'; // Agregar sombra al elemento clonado
    cloneElement.style.zIndex = '12';

    // Añadir la copia al DOM
    document.body.appendChild(cloneElement);

    // Establecer la copia como el elemento arrastrado
    setDraggedArtist(cloneElement);

    // Guardar la posición del ratón con respecto al elemento arrastrado
    setMouseOffset({ x: offsetX, y: offsetY });

    setDraggedArtistData(value);
    setIsDragging(true);
  };
  
  const handleMouseMove = (event: MouseEvent) => {
    if (draggedArtist) {
      // Calcular la nueva posición del elemento arrastrado en relación con la posición del ratón
      const newX = event.clientX - mouseOffset.x;
      const newY = event.clientY - mouseOffset.y;

      // Actualizar la posición del elemento arrastrado
      draggedArtist.style.left = `${newX}px`;
      draggedArtist.style.top = `${newY}px`;
      const selectedArtistsDiv = document.getElementById('selectedArtists');
      if (selectedArtistsDiv && event.clientX >= selectedArtistsDiv.offsetLeft && event.clientX <= (selectedArtistsDiv.offsetLeft + selectedArtistsDiv.offsetWidth) && event.clientY >= selectedArtistsDiv.offsetTop && event.clientY <= (selectedArtistsDiv.offsetTop + selectedArtistsDiv.offsetHeight)) {
        isDraggingOver[0] = true;
      } else {
        isDraggingOver[0] = false;
      }
    }
  };

  const handleMouseUp = () => {
    if (draggedArtist) {
      draggedArtist.remove()
      if (isDraggingOver[0] && !selectedArtists.some((artist) => artist.id === draggedArtistData.id)) {
        selectedArtists.push(draggedArtistData)
      }
      setDraggedArtistData(null)
    }
    setDraggedArtist(null);
    setIsDragging(false);
  };

  useEffect(() => {
    // Agregar eventos de mouse globales para manejar el arrastrar y soltar
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      // Limpiar eventos de mouse cuando el componente se desmonte
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [draggedArtist]);

  const handleInputChange = (event: any) => {
    setInputValue(event.target.value);
    if (event.target.value === '') {
      searchState.object = []
    }
  };

  const handleClearButtonClick = () => {
    setInputValue('');
    searchState.object = []
  };

  const handleDeleteArtist = (artistId: string) => {
    // Filtrar la lista de artistas para eliminar el que tiene el ID proporcionado
    const updatedArtists = selectedArtists.filter((artist) => artist.id !== artistId);
    // Actualizar el estado con la nueva lista de artistas sin el eliminado
    setSelectedArtists(updatedArtists);
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (inputValue !== '') {
        document.getElementById('searchButton')?.click();
      }
    }, 500);
  
    return () => clearTimeout(timeoutId); // Limpiar el timeout en cada renderización
  }, [inputValue]);

  useEffect(() => {
    setArtistsFound(searchState.object.length !== 0)
  }, [searchState.object])

  return (
    <div className="text-center">
      <h1 className="text-3xl font-bold mb-8">Zempui&apos;s playlist generator</h1>
      {loggedIn && 
      <div className="mx-auto flex flex-col items-center">
        <form className="mt-8 flex flex-col items-center" action={formCreatePlaylistAction}>
          <input type="text" required={true} name="playlistName" placeholder="Nombre de la playlist" className="text-center py-2 px-4 mb-4 rounded-md focus:outline-none border border-gray-300 placeholder-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500" />
          <input type="hidden" name="selectedArtists" value={JSON.stringify(selectedArtists)} />
          <SubmitButton
            id="playlistGeneratorButton"
            defaultText="Genera tu playlist"
            pendingText="Generando playlist..."
            disabled={selectedArtists.length === 0}
            className="py-3 px-6 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 transition-colors duration-300 disabled:opacity-50"
          />
        </form>
      </div>}
      <div className="mx-auto flex">
        {!loggedIn && (
          <div className="mx-auto flex flex-col items-center">
            <form action={formLoginAction} className="mb-4">
              <SubmitButton id='loginButton' defaultText="Inicia sesión con Spotify" pendingText="Serás redirigido en breve..."
                className="py-3 px-6 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-600 transition-colors duration-300 disabled:opacity-50" />
            </form>
          </div>
        )}

        {loggedIn && (<>
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              backgroundColor: 'rgba(0, 0, 0, 0.25)',
              transition: 'opacity 0.3s ease',
              opacity: isDragging ? 1 : 0,
              zIndex: 10,
              pointerEvents: 'none',
            }}
          />
          <div className="w-1/2 m-4"
          style={{ minWidth: 'fit-content' }}>
          <form action={formSearchAction} className="mb-4">
            <div className={`flex items-center border rounded-md overflow-hidden ${isInputFocused ? 'border-blue-500' : 'border-gray-300'}`}>
              <input
                autoComplete="off"
                id="query"
                name="query"
                type="text"
                onFocus={handleInputFocus}
                onBlur={handleInputBlur}
                value={inputValue}
                onChange={handleInputChange}
                className="py-2 px-4 flex-grow focus:outline-none"
                placeholder="Buscar..."
              />
              {inputValue && (
                <button
                  onClick={handleClearButtonClick}
                  className="text-gray-600 px-4 py-2 rounded-full focus:outline-none hover:bg-gray-200 transition-colors duration-300 flex items-center justify-center"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              )}
            </div>
            <SubmitButton id='searchButton' defaultText="" pendingText="" />
          </form>

          <div className="mb-4">
          {artistsFound &&
          
            searchState.object.map((value: any) => (
              <div
                key={value.id}
                className="flex items-center bg-white rounded-lg p-4 cursor-pointer mb-4 border border-gray-300 hover:shadow-md"
                onMouseDown={(e) => handleMouseDown(value, e)}
              >
                <img src={value.image.url} alt={value.name} className="h-16 w-16 rounded-full mr-4" />
                <p className="text-lg">{value.name}</p>
              </div>
            ))}
            </div>
        </div>

        <div
          className="w-1/2 border rounded-md p-4 overflow-auto my-4 mx-6 bg-white"
          id="selectedArtists"
          style={{ height: '100vh', minWidth: 'fit-content', zIndex: 11}}
        >
          <h2>Artistas seleccionados:</h2>
          <div className="mb-4">
            {selectedArtists.map((artist) => (
              <div
                key={artist.id}
                className="flex items-center bg-white rounded-lg p-4 mt-4 border border-gray-300 relative"
              >
                <img src={artist.image.url} alt={artist.name} className="h-16 w-16 rounded-full mr-4" />
                <p className="text-lg">{artist.name}</p>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-12 w-12 p-2 absolute rounded-full top-1/2 focus:outline-none -translate-y-1/2 right-4 cursor-pointer text-gray-400 hover:text-gray-600 hover:bg-gray-200 transition-colors duration-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  onClick={() => handleDeleteArtist(artist.id)}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              
            ))}
          </div>
        </div>

        </>)}
      </div>
    </div>
  );
}
