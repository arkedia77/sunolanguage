// 화면 텍스트 판독기 — macOS Vision OCR CLI.
//
// ★배경: 유튜브 STT 자막은 영어 태그를 한글 음차로 뭉갠다("스포큰 온", "익스클루드 스타일").
// 브라켓 철자 원문은 화면에만 있으므로, 프레임을 떠서 화면 글자를 직접 읽어야 한다.
// 즉 여기서 0줄이 나와도 「태그 없음」이 아니라 「그 프레임엔 안 보임」이다.
//
// 빌드: swiftc -O scripts/ocr_frames.swift -o .venv/bin/ocr_frames
// 사용: ocr_frames <이미지경로...>   → "파일경로\t신뢰도\t인식문자열" 탭구분 출력

import Foundation
import Vision
import AppKit

func ocr(_ path: String) {
    guard let img = NSImage(contentsOfFile: path),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        FileHandle.standardError.write("LOAD_FAIL\t\(path)\n".data(using: .utf8)!)
        return
    }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    // 한국어 나레이션 자막과 영어 태그가 한 화면에 섞여 나온다 — 둘 다 켠다.
    req.recognitionLanguages = ["en-US", "ko-KR"]
    req.usesLanguageCorrection = false  // 태그 철자를 사전으로 교정당하면 원문이 훼손된다
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    do {
        try handler.perform([req])
    } catch {
        FileHandle.standardError.write("OCR_FAIL\t\(path)\t\(error)\n".data(using: .utf8)!)
        return
    }
    let obs = req.results ?? []
    for o in obs {
        guard let top = o.topCandidates(1).first else { continue }
        let line = top.string.replacingOccurrences(of: "\t", with: " ")
        print("\(path)\t\(String(format: "%.2f", top.confidence))\t\(line)")
    }
}

for path in CommandLine.arguments.dropFirst() {
    ocr(path)
}
