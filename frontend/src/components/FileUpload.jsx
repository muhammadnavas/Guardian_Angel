import { useState, useRef } from 'react';

export default function FileUpload({ onFileSelect, disabled }) {
    const [dragover, setDragover] = useState(false);
    const [preview, setPreview] = useState(null);
    const [fileName, setFileName] = useState('');
    const inputRef = useRef(null);

    const handleFile = (file) => {
        if (!file || !file.type.startsWith('image/')) return;
        setFileName(file.name);
        const reader = new FileReader();
        reader.onload = (e) => setPreview(e.target.result);
        reader.readAsDataURL(file);
        onFileSelect(file);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragover(false);
        handleFile(e.dataTransfer.files[0]);
    };

    const removeFile = (e) => {
        e.stopPropagation();
        setPreview(null);
        setFileName('');
        onFileSelect(null);
        if (inputRef.current) inputRef.current.value = '';
    };

    return (
        <div
            className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-250 bg-white/[0.04]
        ${dragover ? 'border-primary-light bg-primary-light/[0.06] shadow-[0_0_30px_rgba(99,102,241,0.1)]' : 'border-white/15 hover:border-primary-light hover:bg-primary-light/[0.06]'}`}
            onDragOver={(e) => { e.preventDefault(); setDragover(true); }}
            onDragLeave={() => setDragover(false)}
            onDrop={handleDrop}
            onClick={() => !disabled && inputRef.current?.click()}
        >
            <input
                type="file"
                ref={inputRef}
                accept="image/*"
                onChange={(e) => handleFile(e.target.files[0])}
                disabled={disabled}
                className="hidden"
            />

            {!preview ? (
                <>
                    <span className="text-6xl block mb-4 animate-float">📸</span>
                    <h3 className="font-heading text-xl font-bold mb-2">Upload a Screenshot</h3>
                    <p className="text-gray-400">
                        Drag & drop an image here or <span className="text-primary-light font-semibold underline">browse files</span>
                    </p>
                    <p className="mt-2 text-sm text-gray-500">Supports PNG, JPG, WEBP</p>
                </>
            ) : (
                <div className="inline-block rounded-xl overflow-hidden border border-white/[0.08] relative max-w-full">
                    <img src={preview} alt="Upload preview" className="max-h-[300px] object-contain block" />
                    <button
                        className="absolute top-2 right-2 w-8 h-8 rounded-full bg-black/70 text-white flex items-center justify-center text-lg border border-white/[0.08] hover:bg-danger transition-colors cursor-pointer"
                        onClick={removeFile}
                        title="Remove"
                    >
                        ✕
                    </button>
                    <div className="px-3 py-2 bg-surface text-sm text-gray-400 border-t border-white/[0.08]">
                        {fileName}
                    </div>
                </div>
            )}
        </div>
    );
}
