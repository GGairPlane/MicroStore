//
//  ExplorerViewController.swift
//  MicroStore
//
//  Created by Tomer Volloch on 11/04/2023.
//

import UIKit

var toCopy: String = ""
var toCut: String = ""

class ExplorerViewController: UIViewController {

    
    
    @IBOutlet weak var backButton: UIButton!
    
    
    @IBOutlet weak var tableView: UITableView!
    
    var dirs: [String] = []
    var files: [String] = []
    
    var currPath: String = ""
    
    var isLoading = false
    let activityIndicator = UIActivityIndicatorView(style: .medium)
    
    
    
    func scrollViewDidScroll(_ scrollView: UIScrollView) {
        if scrollView.contentOffset.y == -4 && !isLoading{
            isLoading = true
            
            Task {
                let (dirs, files) = await sock.getDir(path: currPath)
                self.dirs = dirs
                self.files = files
                self.tableView.reloadData()
            }
        }
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        tableView.dataSource = self
        tableView.delegate = self
        backButton.isHidden = currPath.isEmpty

        
        Task{
            let (dirs, files) = await sock.getDir(path: currPath)
            
            DispatchQueue.main.async {
                self.dirs = dirs
                self.files = files
                self.tableView.reloadData()
            }
        }
    }
    
    @IBAction func backButtonTapped(_ sender: UIButton) {
        navigationController?.popViewController(animated: true)
        
        

    }
    
    
    
    @IBAction func openMenu(_ sender: UIButton) {
        let uploadFileAction = UIAction(title: "Upload File") { _ in
               // Handle file upload
           }

           let pasteCopiedAction = UIAction(title: "Paste Copied") { _ in
               // Handle pasting copied item
           }

           let makeNewDirAction = UIAction(title: "Make New Directory") { _ in
               // Handle creating a new directory
           }

           let logoutAction = UIAction(title: "Logout", attributes: .destructive) { _ in
               // Handle logout
           }

           let menu = UIMenu(title: "", children: [uploadFileAction, pasteCopiedAction, makeNewDirAction, logoutAction])
           sender.menu = menu
           sender.showsMenuAsPrimaryAction = true
    }
    
    
}

extension ExplorerViewController :  UITableViewDataSource, UITableViewDelegate{
    
    func numberOfSections(in tableView: UITableView) -> Int {
        return 2
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return section == 0 ? dirs.count : files.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell =  tableView.dequeueReusableCell(withIdentifier: "fileCell", for: indexPath)
        cell.textLabel?.font = UIFont.boldSystemFont(ofSize: 16.0)
        if indexPath.section == 0 {
            cell.textLabel?.text = dirs[indexPath.row]
            cell.detailTextLabel?.text = "<DIR>"
            cell.detailTextLabel?.font = UIFont.boldSystemFont(ofSize: 16.0)

            
        } else {
            cell.textLabel?.text = files[indexPath.row]
            cell.detailTextLabel?.text = ""

        }
        print(files)
        return cell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        
        let isDirectory = indexPath.section == 0
        let itemName = isDirectory ? dirs[indexPath.row] : files[indexPath.row]
        
        let actionSheet = UIAlertController(title: nil, message: "Choose an action for \(itemName)", preferredStyle: .actionSheet)
        
        if isDirectory {
            let enterAction = UIAlertAction(title: "Enter", style: .default) { _ in
                let explorerViewController = UIStoryboard(name: "Main", bundle: nil).instantiateViewController(withIdentifier: "explorer_controller") as! ExplorerViewController
                    explorerViewController.currPath = self.currPath  + itemName + "/"
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
                    
                    for permission in ["Viewer", "Editor"] {
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
            }
        }
        
        let copyAction = UIAlertAction(title: "Copy", style: .default) { _ in
            toCopy = self.currPath + itemName
            toCut = ""
            }
        
        let cutAction = UIAlertAction(title: "Cut", style: .default) { _ in
            toCut = self.currPath + itemName
            toCopy = ""
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