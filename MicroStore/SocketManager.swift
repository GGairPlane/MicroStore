//
//  SocketManager.swift
//  MicroStore
//
//  Created by Tomer Volloch on 22/04/2023.
//

import Foundation
import Darwin
import CryptoSwift
import CommonCrypto


let SIZE_HEADER_FORMAT = "000000000|"
let SIZE_HEADER_SIZE = SIZE_HEADER_FORMAT.count
let TCP_DEBUUG = true
let LEN_TO_PRINT = 100


public class SocketManager {
    public static let shared = SocketManager()
    
    //    private let socketQueue = DispatchQueue(label: "socketQueue")
    private(set) var socketFD: Int32 = -1
    private var cipher: String?
    
    private init() {}
    
    
    
    public func connect(host: String, port: UInt16) async -> Void{
        self.socketFD = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        
        var serverAddress = sockaddr_in()
        serverAddress.sin_family = sa_family_t(AF_INET)
        serverAddress.sin_port = UInt16(port).bigEndian
        inet_pton(AF_INET, host, &serverAddress.sin_addr)
        
        _ = withUnsafePointer(to: &serverAddress) {
            $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                Darwin.connect(socketFD, $0, socklen_t(MemoryLayout<sockaddr_in>.size))
            }
        }
    }
    
    
    public func send(_ data: Data) {
        let headerData = String(format: "%0\(SIZE_HEADER_SIZE - 1)d|", data.count)
        let combinedData = headerData.data(using: .utf8)! + data
        
        let _ = combinedData.withUnsafeBytes { (bytes: UnsafeRawBufferPointer) -> Int in
            if let baseAddress = bytes.baseAddress {
                return Darwin.send(socketFD, baseAddress, combinedData.count, 0)
            } else {
                return 0
            }
        }
        if TCP_DEBUUG && data.count > 0 {
            print("\nSent(\(data.count))>>>", combinedData.prefix(LEN_TO_PRINT).asciiEncodedString())
        }
    }
    
    
    public func recv() async -> Data? {
        
        var sizeHeader = Data()
        var dataLen = 0
        
        while sizeHeader.count < SIZE_HEADER_SIZE {
            var buffer = [UInt8](repeating: 0, count: SIZE_HEADER_SIZE - sizeHeader.count)
            let bytesRead = Darwin.recv(socketFD, &buffer, buffer.count, 0)
            
            if bytesRead == 0{
                sizeHeader = Data()
                break
            }
            
            sizeHeader.append(contentsOf: buffer)
        }
        
        var data = Data()
        if !sizeHeader.isEmpty {
            if let sizeString = String(data: sizeHeader.prefix(SIZE_HEADER_SIZE - 1), encoding: .utf8),
               let dataSize = Int(sizeString) {
                dataLen = dataSize
            } else {
                dataLen = 0
            }
            
            while data.count < dataLen {
                var buffer = [UInt8](repeating: 0, count: dataLen - data.count)
                print("len: \(buffer.count)")
                let bytesRead = Darwin.recv(socketFD, &buffer, buffer.count, 0)

                if bytesRead == 0 {
                    data = Data()
                    break
                }
                data.append(contentsOf: buffer.prefix(bytesRead))
            }
            
        }
        
        if TCP_DEBUUG && !sizeHeader.isEmpty {
            print("\nRecv(\(data.count))>>>", sizeHeader.asciiEncodedString() +  data.prefix(LEN_TO_PRINT).asciiEncodedString())
        }
        
        if dataLen != data.count {
            data = Data() //partial data is like no data!
        }
        
        return data
        
    }
    
    public func close(){
        Darwin.close(socketFD)
    }
}
public class SecureSocketManager {
    // Add a private var cipher of the type AESCipher
    private var cipher: AESCipher?
    private let socket = SocketManager.shared
    
    public init() {}
    
    // Override the connect method to include Diffie-Hellman key exchange
    public func connect(host: String, port: UInt16) async throws {
        // Call the original connect method
        await socket.connect(host: host, port: port)
        // Perform Diffie-Hellman key exchange
        guard let key = await dh()
        else {throw SocketError.connectionError}
        cipher = AESCipher(key: key)

    }
    
    // Override the send method to encrypt data using the cipher
    public func send(_ data: Data) {
        print("\nC LOG:Sent >>> ", data.prefix(LEN_TO_PRINT).asciiEncodedString())
        if let cipher = cipher {
            let encryptedData = cipher.encrypt(data: data)
            socket.send(encryptedData!)
        } else {
            socket.send(data)
        }
    }
    
    // Override the recv method to decrypt data using the cipher
    public func recv() async -> Data? {
        if let encryptedData = await socket.recv(), let cipher = cipher {
            let decryptedData = cipher.decrypt(data: encryptedData)
            print("\nC LOG:Recieved <<< ", decryptedData?.prefix(LEN_TO_PRINT).asciiEncodedString() ?? "no data")
            return decryptedData
        } else {
            return await socket.recv()
        }
    }
    
    public func close() {
        socket.close()
    }
    
    private func dh() async -> String? {
        guard let p = Int(String(decoding: await socket.recv()!, as: UTF8.self))
            else {return nil}
        let g = Int.random(in: 1..<p)
        socket.send(Data(String(g).utf8))
        let secret = Int.random(in: 1..<g)
        let b = modPow(base: g, expo: secret, mod: p)
        guard let a = Int(String(decoding: await socket.recv()!, as: UTF8.self))
            else {return nil}
        socket.send(Data(String(b).utf8))
        return String(modPow(base: a, expo: secret, mod: p))
    }
    
    private func modPow(base: Int, expo: Int, mod: Int) -> Int {
        if mod == 1 { return 0 }
        var result = 1
        var b = base % mod
        var e = expo
        while e > 0 {
            if e & 1 == 1 { result = (result * b) % mod }
            e >>= 1
            b = (b * b) % mod
        }
        return result
    }
    
}


class AESCipher {
    private let key: Data
    
    init(key: String) {
        self.key = AESCipher.sha256(string: key)
    }
    
    func encrypt(data: Data) -> Data? {
            let iv = AES.randomIV(AES.blockSize)
            do {
                let aes = try AES(key: key.bytes, blockMode: CBC(iv: iv), padding: .pkcs7)
                let encryptedBytes = try aes.encrypt(data.bytes)
                let combinedBytes = iv + encryptedBytes
                return Data(combinedBytes)
            } catch {
                print("Encryption error: \(error.localizedDescription)")
                return nil
            }
        }
        
        func decrypt(data: Data) -> Data? {
            let iv = data[0..<AES.blockSize].bytes
            let encryptedBytes = data[AES.blockSize...].bytes
            
            do {
                let aes = try AES(key: key.bytes, blockMode: CBC(iv: iv), padding: .pkcs7)
                let decryptedBytes = try aes.decrypt(encryptedBytes)
                return Data(decryptedBytes)
            } catch {
                print("Decryption error: \(error.localizedDescription)")
                return nil
            }
        }


    private static func sha256(string: String) -> Data {
        let data = Data(string.utf8)
        var hash = Data(count: Int(CC_SHA256_DIGEST_LENGTH))
        _ = data.withUnsafeBytes { dataBytes in
            hash.withUnsafeMutableBytes { hashBytes in
                CC_SHA256(dataBytes.baseAddress, CC_LONG(data.count), hashBytes.bindMemory(to: UInt8.self).baseAddress)
            }
        }
        return hash
    }
}


extension SecureSocketManager {
    func login(username: String, password: String) async -> String {
        let toSend = "LOGIN~\(username)~\(password)"
        send(Data(toSend.utf8))
        let response = String(data: await recv()!, encoding: .utf8)
        if response!.prefix(5) == "LOGAK" {
            return "success"
        }
        else {
            return response?.replacingOccurrences(of: "~", with: ":") ?? "connection error"
        }
        
    }
    
    func signup(username: String, password: String) async -> String {
        let toSend = "SGNUP~\(username)~\(password)"
        send(Data(toSend.utf8))
        let response = String(data: await recv()!, encoding: .utf8)
        if response!.prefix(5) == "LOGAK" {
            return "success"
        }
        else {
            return response?.replacingOccurrences(of: "~", with: ":") ?? "connection error"
        }
        
    }
    
    func getDir(path: String) async -> ([String], [String]) {
        let command = "CHGDR~\(path)"
        send(Data(command.utf8))
        let data = await recv()
        
        guard let response = String(data: data!, encoding: .utf8),
              response.hasPrefix("RECHD~") else {
            return ([], [])
        }
        
        let jsonResponse = response.dropFirst("RECHD~".count)
        
        do {
            if let jsonData = jsonResponse.data(using: .utf8),
               let content = try JSONSerialization.jsonObject(with: jsonData, options: []) as? [[String]] {
                
                let directories = content[0]
                let files = content[1]
                
                return (directories, files)
            }
        } catch {
            print("JSON parsing error: \(error)")
        }
        
        return ([], [])
    }
    
    
    func getShared() async -> [SharedItem] {
        let command = "GTSHR~"
        send(Data(command.utf8))
        let data = await recv()
        
        guard let response = String(data: data!, encoding: .utf8),
              response.hasPrefix("REGTS~") else {
            return []
        }
        
        let jsonResponse = response.dropFirst("REGTS~".count)
        
        do {
            if let jsonData = jsonResponse.data(using: .utf8),
               let sharedContent = try JSONSerialization.jsonObject(with: jsonData, options: []) as? [[String]] {
                                
                let files = sharedContent.map { item -> SharedItem in
                    SharedItem(name: item[0], perm: item[1], uuid: item[2])
                }
                
                return files
            }
        } catch {
            print("JSON parsing error: \(error)")
        }
        
        return []
    }
    
    
    func rename(oldName: String, newName: String) async -> String {
        let command = "CHGNM~\(oldName)~\(newName)"
        send(Data(command.utf8))
        let data = await recv()
        guard let response = String(data: data!, encoding: .utf8) else {
            return "connection error"
        }
        
        if response.hasPrefix("CHGAK~"){
            return "success"
        }
        else {
            return response.replacingOccurrences(of: "~", with: ":")
        }
    }
    
    
    func remove(path: String) async -> String {
        let command = "REMOV~\(path)"
        send(Data(command.utf8))
        let data = await recv()
        guard let response = String(data: data!, encoding: .utf8) else {
            return "connection error"
        }
        
        if response.hasPrefix("REMAK~"){
            return "success"
        }
        else {
            return response.replacingOccurrences(of: "~", with: ":")
        }
    }
    
    
    func download(path: String) async -> (String, Data?) {
        let command = "DWNLD~\(path)"
        send(Data(command.utf8))
        guard let data = await recv() else {
            return ("connection error", nil)
        }
        
        let separator: UInt8 = 0x7E  // ASCII for "~"
        var separatorIndices = [Int]()
        for (index, byte) in data.enumerated() {
            if byte == separator {
                separatorIndices.append(index)
                if separatorIndices.count == 2 {
                    break
                }
            }
        }
        
        guard separatorIndices.count == 2 else {
            return ("Invalid response format", nil)
        }
        
        let prefixData = data.subdata(in: 0..<separatorIndices[0])
        let filenameData = data.subdata(in: (separatorIndices[0] + 1)..<separatorIndices[1])
        let fileData = data.subdata(in: (separatorIndices[1] + 1)..<data.count)
        if let prefix = String(data: prefixData, encoding: .utf8), prefix == "REDWN" {
            if let fullname = String(data: filenameData, encoding: .utf8) {
                
                let filename = URL(fileURLWithPath: fullname.replacingOccurrences(of: "\\", with: "/")).lastPathComponent

                return (filename, fileData)
            } else {
                return ("Invalid filename", nil)
            }
        } else {
            if let errorMessage = String(data: prefixData, encoding: .utf8) {
                return (errorMessage.replacingOccurrences(of: "~", with: ":"), nil)
            } else {
                return ("Unknown error", nil)
            }
        }
    }
    
    
    func share(name: String, path: String, perm: String) async -> String {
        let command = "SHARE~\(name)~\(path)~\(perm)"
        send(Data(command.utf8))
        let data = await recv()
        guard let response = String(data: data!, encoding: .utf8) else {
            return "connection error"
        }
        
        if response.hasPrefix("SHRAK~"){
            return "success"
        }
        else {
            return response.replacingOccurrences(of: "~", with: ":")
        }
    }
    
    
    func upload(fileName: String, fileData: Data) async -> String {
            let command = "UPLOD~\(fileName)~"
            let commandData = Data(command.utf8)

            var combinedData = commandData
            combinedData.append(fileData)
            send(combinedData)

            let data = await recv()
            guard let response = String(data: data!, encoding: .utf8) else {
                return "connection error"
            }

            if response.hasPrefix("UPLAK~") {
                return "success"
            } else {
                return response.replacingOccurrences(of: "~", with: ":")
            }
        }
    
    
    func newDir(name: String) async -> String {
        let command = "MKDIR~\(name)"
        send(Data(command.utf8))
        let data = await recv()
        guard let response = String(data: data!, encoding: .utf8) else {
            return "connection error"
        }
        
        if response.hasPrefix("MKDAK~"){
            return "success"
        }
        else {
            return response.replacingOccurrences(of: "~", with: ":")
        }
    }
    
    
    func paste(copy: Bool, sourcePath: String, destinationPath: String) async -> String {
        let command = copy ? "COPYP~\(sourcePath)~\(destinationPath)" : "MOVFL~\(sourcePath)~\(destinationPath)"
        let expected = copy ? "COPAK~" : "MOVAK~"
        send(Data(command.utf8))
        let data = await recv()
        guard let response = String(data: data!, encoding: .utf8) else {
            return "connection error"
        }
        
        if response.hasPrefix(expected){
            return "success"
        }
        else {
            return response.replacingOccurrences(of: "~", with: ":")
        }
    }
    
    func logout() {
        let command = "EXITT~goodbye"
        send(Data(command.utf8))
        close()
    }
    
    
}

enum SocketError : Error {
    case connectionError
}


import Foundation
import CryptoKit

func md5Checksum(data: Data) -> String {
    let digest = Insecure.MD5.hash(data: data)
    return digest.map { String(format: "%02hhx", $0) }.joined()
}

extension Data {
    func asciiEncodedString() -> String {
        return self.reduce("") { (result, byte) -> String in
            if (32...126).contains(byte) {
                return result + String(UnicodeScalar(byte))
            } else {
                return result + String(format: "\\x%02x", byte)
            }
        }
    }
}
