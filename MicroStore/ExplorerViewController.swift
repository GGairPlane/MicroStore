import UIKit
import UniformTypeIdentifiers

// Global variables used for copy and cut
var copyName: String = ""
var cutName: String = ""
var sourceID: String = ""

// This is the main View Controller that is responsible for the File Explorer UI
class ExplorerViewController: UIViewController {
    
    @IBOutlet weak var backButton: UIButton!
    @IBOutlet weak var tableView: UITableView!
    
    // Lists to hold directory and file names
    var dirs: [String] = []
    var files: [String] = []
    
    // Holds the current path the user is viewing
    var currPath: String = ""
    
    // This function fetches the current directory's content and refreshes the TableView
    func refreshData() {
        Task {
            let (dirs, files) = await sock.getDir(path: currPath)
            DispatchQueue.main.async {
                self.dirs = dirs
                self.files = files
                self.tableView.reloadData()
            }
        }
    }
    
    // Called when the view is initially loaded
    override func viewDidLoad() {
        super.viewDidLoad()
        
        tableView.dataSource = self
        tableView.delegate = self
        backButton.isHidden = currPath.isEmpty
    }
    
    // Called when the view is about to be added to a view hierarchy
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        refreshData()
    }
    
    // Action performed when the back button is tapped
    @IBAction func backButtonTapped(_ sender: UIButton) {
        navigationController?.popViewController(animated: true)
    }
}

// Extension for implementing TableView delegate and datasource methods
extension ExplorerViewController :  UITableViewDataSource, UITableViewDelegate{
    
    // Define the number of sections in the table view
    func numberOfSections(in tableView: UITableView) -> Int {
        return 2
    }
    
    // Define the number of rows in each section of the table view
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return section == 0 ? dirs.count : files.count
    }
    
    // Provide a cell object for each row
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell =  tableView.dequeueReusableCell(withIdentifier: "fileCell", for: indexPath)
        cell.textLabel?.font = UIFont.boldSystemFont(ofSize: 16.0)
        
        if indexPath.section == 0 { // if the cell is for directory
            cell.textLabel?.text = dirs[indexPath.row]
            cell.detailTextLabel?.text = "<DIR>"
            cell.detailTextLabel?.font = UIFont.boldSystemFont(ofSize: 16.0)

            
        } else { // if the cell is for file
            cell.textLabel?.text = files[indexPath.row]
            cell.detailTextLabel?.text = ""

        }
        return cell
    }
    
    // Handle cell selection
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        
        let isDirectory = indexPath.section == 0
        let itemName = isDirectory ? dirs[indexPath.row] : files[indexPath.row]
        
        let actionSheet = UIAlertController(title: nil, message: "Choose an action for \(itemName)", preferredStyle: .actionSheet)
        
        if isDirectory {
            let enterAction = UIAlertAction(title: "Enter", style: .default) { _ in
                let explorerViewController = UIStoryboard(name: "Main", bundle: nil).instantiateViewController(withIdentifier: "explorer_controller") as! ExplorerViewController
                    explorerViewController.currPath = self.currPath  + itemName + "\\"
                    explorerViewController.hidesBottomBarWhenPushed = false
                    self.navigationController?.pushViewController(explorerViewController, animated: true)
            }
            actionSheet.addAction(enterAction)
        }
        
        else {
            
            let downloadAction = UIAlertAction(title: "Download", style: .default) { _ in
                Task {
                    let (result, fileData) = await sock.download(path: self.currPath + itemName)
                    if result == itemName, let data = fileData {
                        DispatchQueue.main.async {
                            let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent(itemName)
                            do {
                                try data.write(to: tempURL)
                                let activityViewController = UIActivityViewController(activityItems: [tempURL], applicationActivities: nil)
                                self.present(activityViewController, animated: true, completion: nil)
                            } catch {
                                let alertController = UIAlertController(title: "Error", message: "Failed to save the file locally.", preferredStyle: .alert)
                                alertController.addAction(UIAlertAction(title: "OK", style: .default))
                                self.present(alertController, animated: true)
                            }
                        }
                    } else {
                        DispatchQueue.main.async {
                            let alertController = UIAlertController(title: "Error", message: result, preferredStyle: .alert)
                            alertController.addAction(UIAlertAction(title: "OK", style: .default))
                            self.present(alertController, animated: true)
                        }
                    }
                }

            }
            
            let shareAction = UIAlertAction(title: "Share", style: .default) { _ in
                let alertController = UIAlertController(title: "Share File", message: "Enter the username and choose the permission level.", preferredStyle: .alert)
                
                alertController.addTextField { textField in
                    textField.placeholder = "Username"
                }
                
                alertController.addAction(UIAlertAction(title: "Share", style: .default) { _ in
                    guard let username = alertController.textFields?.first?.text, !username.isEmpty else {
                        return
                    }
                    
                    let permissionActionSheet = UIAlertController(title: "Choose Permission", message: nil, preferredStyle: .actionSheet)
                    
                    for permission in ["viewer", "editor"] {
                        permissionActionSheet.addAction(UIAlertAction(title: permission, style: .default) { _ in
                            Task { let result = await sock.share(name: username, path: self.currPath+itemName, perm: permission)
                                if result != "success" {
                                    DispatchQueue.main.async {
                                        let alertController = UIAlertController(title: "Error", message: result, preferredStyle: .alert)
                                        alertController.addAction(UIAlertAction(title: "OK", style: .default))
                                        self.present(alertController, animated: true)
                                    }
                                    return
                                }
                            }
                        })
                    }
                    
                    permissionActionSheet.addAction(UIAlertAction(title: "Cancel", style: .cancel))
                    
                    self.present(permissionActionSheet, animated: true)
                })
                
                alertController.addAction(UIAlertAction(title: "Cancel", style: .cancel))
                
                self.present(alertController, animated: true)
            }
            
            actionSheet.addAction(downloadAction)
            actionSheet.addAction(shareAction)
        }
        
        let removeAction = UIAlertAction(title: "Remove", style: .default) { _ in
            Task { let result = await sock.remove(path: self.currPath + itemName)
                if result != "success" {
                    DispatchQueue.main.async {
                        let alertController = UIAlertController(title: "Error", message: result, preferredStyle: .alert)
                        alertController.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(alertController, animated: true)
                    }
                    return
                }
                self.refreshData()
            }
        }
        
        let copyAction = UIAlertAction(title: "Copy", style: .default) { _ in
            copyName = self.currPath + itemName
            cutName = ""
            sourceID = ""
        }
        
        let cutAction = UIAlertAction(title: "Cut", style: .default) { _ in
            cutName = self.currPath + itemName
            copyName = ""
            sourceID = ""
        }
        
        let changeNameAction = UIAlertAction(title: "Rename", style: .default) { _ in
            let alertController = UIAlertController(title: "Share File", message: "Enter the username and choose the permission level.", preferredStyle: .alert)
            
            alertController.addTextField { textField in
                textField.text = itemName
                textField.placeholder = "New name"
            }
            
            alertController.addAction(UIAlertAction(title: "Rename", style: .default) { _ in
                guard let newName = alertController.textFields?.first?.text, !newName.isEmpty else {
                    return
                }
                Task { let result = await sock.rename(oldName: self.currPath+itemName, newName: self.currPath+newName)
                    if result != "success" {
                        DispatchQueue.main.async {
                            let alertController = UIAlertController(title: "Error", message: result, preferredStyle: .alert)
                            alertController.addAction(UIAlertAction(title: "OK", style: .default))
                            self.present(alertController, animated: true)
                        }
                        return
                    }
                    self.refreshData()
                }
                
            })
            
            alertController.addAction(UIAlertAction(title: "Cancel", style: .cancel))
            
            self.present(alertController, animated: true)
        }
        
        let cancelAction = UIAlertAction(title: "Cancel", style: .cancel, handler: nil)
        
        actionSheet.addAction(removeAction)
        actionSheet.addAction(copyAction)
        actionSheet.addAction(cutAction)
        actionSheet.addAction(changeNameAction)
        actionSheet.addAction(cancelAction)
        
        tableView.deselectRow(at: indexPath, animated: true)
        self.present(actionSheet, animated: true, completion: nil)
    }
}

// Extension for implementing UIDocumentPickerDelegate methods
extension ExplorerViewController : UIDocumentPickerDelegate {
    
    // Action for opening the menu
    @IBAction func openMenu(_ sender: UIButton) {
        let uploadFileAction = UIAction(title: "Upload File") { _ in
            let documentPicker = UIDocumentPickerViewController(forOpeningContentTypes: [UTType.data])
                documentPicker.delegate = self
                documentPicker.modalPresentationStyle = .formSheet
                self.present(documentPicker, animated: true, completion: nil)
           }

       let pasteAction = UIAction(title: "Paste") { _ in
           if !copyName.isEmpty || !cutName.isEmpty {
               let sourcePath = !copyName.isEmpty ? copyName : cutName
               let actualSource = sourceID.isEmpty ? sourcePath : "|\(sourceID)"
               Task {
                   let result = await sock.paste(copy: !copyName.isEmpty, sourcePath: actualSource, destinationPath: self.currPath + URL(fileURLWithPath: sourcePath.replacingOccurrences(of: "\\", with: "/")).lastPathComponent)
                   if result != "success" {
                       DispatchQueue.main.async {
                           let alertController = UIAlertController(title: "Error", message: result, preferredStyle: .alert)
                           alertController.addAction(UIAlertAction(title: "OK", style: .default))
                           self.present(alertController, animated: true)
                       }
                   }
                   self.refreshData()
               }
           }
       }
    
        let makeNewDirAction = UIAction(title: "Make New Directory") { _ in
            let alertController = UIAlertController(title: "Create New Directory", message: "Enter the name for the new directory.", preferredStyle: .alert)
            alertController.addTextField { textField in
                textField.placeholder = "Directory name"
            }
            alertController.addAction(UIAlertAction(title: "Create", style: .default) { _ in
                guard let dirName = alertController.textFields?.first?.text, !dirName.isEmpty else {
                    return
                }
                let forbiddenCharacters = CharacterSet(charactersIn: "/\\:*?\"<>|")
                if dirName.rangeOfCharacter(from: forbiddenCharacters) == nil {
                    Task {
                        let result = await sock.newDir(name: dirName)
                        if result != "success" {
                            DispatchQueue.main.async {
                                let alertController = UIAlertController(title: "Error", message: result, preferredStyle: .alert)
                                alertController.addAction(UIAlertAction(title: "OK", style: .default))
                                self.present(alertController, animated: true)
                            }
                        }
                        self.refreshData()
                    }
                } else {
                    DispatchQueue.main.async {
                        let alertController = UIAlertController(title: "Error", message: "The directory name contains forbidden characters.", preferredStyle: .alert)
                        alertController.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(alertController, animated: true)
                    }
                }
            })
            alertController.addAction(UIAlertAction(title: "Cancel", style: .cancel))
            self.present(alertController, animated: true)
        }

                                         

       let logoutAction = UIAction(title: "Logout", attributes: .destructive) { _ in
           Task {
               sock.logout()
               
               DispatchQueue.main.async {
                   if let navigationController = self.navigationController {
                       navigationController.popToRootViewController(animated: true)

                   }
               }
           }
       }

       let menu = UIMenu(title: "", children: [uploadFileAction, pasteAction, makeNewDirAction, logoutAction])
       sender.menu = menu
       sender.showsMenuAsPrimaryAction = true
    }
    
    
    func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
        guard let url = urls.first else { return }
        
        if url.startAccessingSecurityScopedResource() {
            defer { url.stopAccessingSecurityScopedResource() }
            
            guard let fileData = try? Data(contentsOf: url) else {
                let alertController = UIAlertController(title: "Error", message: "Failed to read the file data", preferredStyle: .alert)
                alertController.addAction(UIAlertAction(title: "OK", style: .default))
                self.present(alertController, animated: true)
                return
            }
            let fileName = url.lastPathComponent
            
            Task {
                let result = await sock.upload(fileName: fileName, fileData: fileData)
                if result != "success" {
                    DispatchQueue.main.async {
                        let alertController = UIAlertController(title: "Error", message: result, preferredStyle: .alert)
                        alertController.addAction(UIAlertAction(title: "OK", style: .default))
                        self.present(alertController, animated: true)
                    }
                }
                self.refreshData()
            }
        }
    }
}
